import os

from loguru import logger

from vikit.video.video import VideoBuildSettings
from vikit.video.video import Video
from vikit.video.composite_video import CompositeVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.video_types import VideoType


class PromptBasedVideo(Video):
    """
    PromptBasedVideo is a simple way to generate a video based out of a text prompt

    It creates a master composite video which embeds as many composite video as there are subtitles
    in the given prompt.

    We do some form of inheritance by composition to prevent circular dependencies and benefit from more modularity
    """

    def __init__(self, prompt=None):
        if prompt is None:
            raise ValueError("prompt cannot be None")
        if len(prompt.subtitles) < 1:
            raise ValueError("No subtitles")

        super().__init__()
        self._prompt = prompt
        self._title = None
        self.metadata.title = self._title
        self._source = type(
            self
        ).__name__  # PromptBasedVideo is made of several composites
        self._inner_composite = None
        self._needs_reencoding = False  # PromptBasedVideo is made of several
        # composites which themselves are made of raw text based video, so no need for reencoding

    def __str__(self) -> str:
        super_str = super().__str__()
        return super_str + os.linesep + f"Prompt: {self._prompt}"

    @property
    def inner_composite(self):
        return self._inner_composite

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.PRMPTBASD)

    def get_title(self):
        """
        Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt
        """
        if not self._title:
            # backup plan: If no title existing yet (should be generated straight from an LLM)
            # then get the first and last words of the prompt
            splitted_prompt = self._prompt.subtitles[0].text.split(" ")
            clean_title_words = [word for word in splitted_prompt if word.isalnum()]
            if len(clean_title_words) == 1:
                summarised_title = clean_title_words[0]
            else:
                summarised_title = clean_title_words[0] + "-" + clean_title_words[-1]
            self._title = summarised_title

        return self._title

    def get_file_name_by_state(self, build_settings: VideoBuildSettings):
        """
        Get the file name of the video

        Returns:
            str: The file name of the video
        """
        return super().get_file_name_by_state(build_settings)

    def build(self, build_settings=VideoBuildSettings()):
        """
        Generate the actual inner video

        Params:
            - build_settings: allow some customization

        Returns:
            The current instance
        """
        super().build(build_settings)

        if self._is_video_generated:
            return self

        build_settings.prompt = self._prompt

        logger.info(
            "Generating several videos from the prompt, this could take some time "
        )
        vid_cp_final = CompositeVideo()
        vid_cp_final._is_root_video_composite = True

        for sub in self._prompt.subtitles:
            vid_cp_sub = CompositeVideo()
            keyword_based_vid, prompt_based_vid, transit = (
                self._build_basic_building_block(sub.text, build_stgs=build_settings)
            )

            vid_cp_sub.append_video(keyword_based_vid).append_video(
                transit
            ).append_video(
                prompt_based_vid
            )  # Building a set of 2 videos around the same text + a transition

            vid_cp_final.append_video(
                vid_cp_sub
            )  # Adding the comnposite to the overall video

        vid_cp_final.build(build_settings=build_settings)

        self._inner_composite = vid_cp_final
        self._is_video_generated = True
        self.metadata = vid_cp_final.metadata
        self._media_url = vid_cp_final.media_url
        self._background_music_file_name = vid_cp_final.background_music

        return self

    def _build_basic_building_block(
        self, sub_text: str, build_stgs: VideoBuildSettings = None
    ):
        """
        build the basic building block of the full video/
        - One RawTextBasedVideo from the keyword
        - One RawTextBasedVideo from the prompt
        - One SeineTransition between the two

        Params:
            - sub_text: the subtitle text
            - build_stgs: the VideoBuildSettings

        Returns:
            - keyword_based_vid: the video generated from the keyword
            - prompt_based_vid: the video generated from the prompt
            - transit: the transition between the two
        """
        keyword_based_vid = RawTextBasedVideo(sub_text).build(
            build_settings=VideoBuildSettings(
                generate_from_llm_keyword=True,
                generate_from_llm_prompt=False,
                test_mode=build_stgs.test_mode,
            )
        )

        prompt_based_vid = RawTextBasedVideo(sub_text).build(
            build_settings=VideoBuildSettings(
                generate_from_llm_prompt=True,
                generate_from_llm_keyword=False,
                test_mode=build_stgs.test_mode,
            )
        )

        transit = SeineTransition(
            source_video=keyword_based_vid,
            target_video=prompt_based_vid,
        )

        return keyword_based_vid, prompt_based_vid, transit
