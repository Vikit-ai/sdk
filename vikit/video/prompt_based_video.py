import os

from vikit.video.video import VideoBuildSettings
from vikit.video.video import Video
from vikit.video.composite_video import CompositeVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.video_types import VideoType
from vikit.prompt.prompt_factory import PromptFactory
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.building.video_building_handler import VideoBuildingHandler


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

    async def compose_inner_composite(self, build_settings: VideoBuildSettings):
        """
        Compose the inner composite video

        Params:
            - build_settings: allow some customization

        Returns:
            The inner composite video
        """
        vid_cp_final = CompositeVideo()
        vid_cp_final._is_root_video_composite = True

        for sub in self._prompt.subtitles:
            vid_cp_sub = CompositeVideo()
            (
                keyword_based_vid,
                prompt_based_vid,
                transit,
            ) = await self._prepare_basic_building_block(
                sub.text, build_stgs=build_settings
            )

            vid_cp_sub.append_video(keyword_based_vid).append_video(
                transit
            ).append_video(
                prompt_based_vid
            )  # Building a set of 2 videos around the same text + a transition

            vid_cp_final.append_video(
                vid_cp_sub
            )  # Adding the comnposite to the overall video

            self._inner_composite = vid_cp_final
        return vid_cp_final

    async def prepare_build(self, build_settings=VideoBuildSettings()):
        """
        Generate the actual inner video

        Params:
            - build_settings: allow some customization

        Returns:
            The current instance
        """
        await super().prepare(build_settings)
        self.inner_composite = await self.compose_inner_composite(
            build_settings=build_settings
        )
        build_settings.prompt = self._prompt

        return self

    def run_post_build_actions(self):
        self.metadata = self.inner_composite.metadata
        self.media_url = self.inner_composite.media_url
        self._background_music_file_name = self.inner_composite.background_music

    async def _prepare_basic_building_block(
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

        prompt_fact = PromptFactory(
            prompt_build_settings=PromptBuildSettings(test_mode=build_stgs.test_mode)
        )
        enhanced_prompt_from_keywords = (
            await prompt_fact.get_reengineered_prompt_from_text(
                prompt=sub_text,
                prompt_build_settings=PromptBuildSettings(
                    test_mode=build_stgs.test_mode
                ),
            )
        )

        keyword_based_vid = await RawTextBasedVideo(sub_text).prepare_build(
            build_settings=VideoBuildSettings(
                prompt=enhanced_prompt_from_keywords,
                test_mode=build_stgs.test_mode,
            )
        )

        enhanced_prompt_from_prompt_text = (
            await prompt_fact.get_reengineered_prompt_from_text(
                prompt=sub_text,
                prompt_build_settings=PromptBuildSettings(
                    test_mode=build_stgs.test_mode
                ),
            )
        )
        prompt_based_vid = await RawTextBasedVideo(sub_text).prepare_build(
            build_settings=VideoBuildSettings(
                prompt=enhanced_prompt_from_prompt_text,
                test_mode=build_stgs.test_mode,
            )
        )
        assert keyword_based_vid is not None, "keyword_based_vid cannot be None"
        assert prompt_based_vid is not None, "prompt_based_vid cannot be None"

        transit = SeineTransition(
            source_video=keyword_based_vid,
            target_video=prompt_based_vid,
        )

        return keyword_based_vid, prompt_based_vid, transit

    def get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        if self._needs_reencoding:
            handlers.append(VideoReencodingHandler())

        return handlers
