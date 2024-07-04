import os

from urllib.request import urlretrieve
from loguru import logger

from vikit.video.video import Video
from vikit.common.decorators import log_function_params
import vikit.common.file_tools as ft
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType


class RawTextBasedVideo(Video):
    """
    Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.
    This is currently the smallest building block available in the SDK, aimed to be used when you want more control
    over the video generation process.
    """

    def __init__(
        self,
        raw_text_prompt: str = None,
        title=None,
    ):
        """
        Initialize the video

        Args:
            raw_text_prompt (str): The raw text prompt to generate the video from
            title (str): The title of the video

        Raises:
            ValueError: If the source media URL is not set
        """
        if not raw_text_prompt:
            raise ValueError("text_prompt cannot be None")
        if len(raw_text_prompt) < 1:
            raise ValueError("No text_prompt provided")

        super().__init__()

        self._text = raw_text_prompt
        self._title = None
        if title:
            self._title = title
        else:
            self._title = self.get_title()
        self._keywords = None
        self._needs_reencoding = False

    def __str__(self) -> str:
        return super().__str__() + os.linesep + f"text: {self._text}"

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWTEXT)

    @log_function_params
    def get_title(self):
        if self._title:
            return self._title
        else:
            # If no title existing yet (should be generated straight from an LLM)
            # then get the first and last words of the prompt
            splitted_prompt = self._text.split(" ")
            clean_title_words = [word for word in splitted_prompt if word.isalnum()]
            if len(clean_title_words) == 1:
                summarised_title = clean_title_words[0]
            else:
                summarised_title = clean_title_words[0] + "-" + clean_title_words[-1]

            # Add a unique identifier suffix to prevent several videos having the same title in a composite down the road
            self._title = summarised_title
            return self._title

    @log_function_params
    def build(
        self,
        build_settings=VideoBuildSettings(),
        excluded_words="",
    ):
        """
        Generate the actual inner video

        Params:
            - build_settings: allow some customization
            - generate_from_keywords: generate the video out of keywords infered from the given prompt, and using an LLM.
            If False, we will generate an enhanced prompt and generate the video out of it
            - excluded_words: words to exclude from the prompt. This is used so as to prevent too much repetition across distant video scenes

        Returns:
            The current instance
        """
        super().build(build_settings)

        if self.metadata.is_video_generated:
            return self

        logger.info("Generating video, could take somne time ")
        enhanced_prompt = None
        ml_gateway = build_settings.get_ml_models_gateway()

        if build_settings.generate_from_llm_keyword:
            # Get more colorfull keywords from prompt, and a title and handle excluded words
            enhanced_prompt, self._title = ml_gateway.get_keywords_from_prompt(
                self._text, excluded_words=excluded_words
            )
            self._keywords = enhanced_prompt
        else:
            # Get more colorfull prompt from current prompt text
            enhanced_prompt, enhanced_title = ml_gateway.get_enhanced_prompt(self._text)
            if self._title is None:
                self._title = ft.get_safe_filename(enhanced_title)
            self._keywords = None

        video_link_from_prompt = ml_gateway.generate_video(
            enhanced_prompt
        )  # Should give a link on the Internet
        self.metadata.is_video_generated = True

        if build_settings.interpolate:
            interpolated_video = ml_gateway.interpolate(video_link_from_prompt)
            self.metadata.is_interpolated = True
            file_name = self.get_file_name_by_state(build_settings)
            interpolated_video_path = urlretrieve(
                interpolated_video,
                file_name,
            )[
                0
            ]  # Then we download it
            self._media_url = interpolated_video_path
            self.metadata.is_interpolated = True
        else:
            file_name = self.get_file_name_by_state(build_settings)
            self._media_url = video_link_from_prompt
        self._source = type(
            ml_gateway
        ).__name__  # The source of the video is used later to decide if we need to reencode the video

        self.metadata.is_interpolated = True

        return self
