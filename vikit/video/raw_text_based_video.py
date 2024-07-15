import os

from vikit.video.video import Video
from vikit.common.decorators import log_function_params
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType

from vikit.video.building.handlers.video_reencoding_handler import (
    VideoBuildingHandlerReencoder,
)
from vikit.video.building.handlers.videogen_handler import (
    VideoBuildingHandlerGenerateFomApi,
)
from vikit.video.building.handlers.interpolation_handler import (
    VideoBuildingHandlerInterpolate,
)
from prompt.building.handlers.prompt_by_raw_user_text_handlers import (
    PromptByRawUserTextHandler,
)
from prompt.building.handlers.prompt_by_keywords_handler import PromptByKeywordsHandler

from vikit.video.building.video_building_handler import VideoBuildingHandler


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
            self.metadata.title = self._title
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
    async def build(
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
        if self.metadata.is_video_generated:
            return self

        if self.are_build_settings_prepared:
            build_settings = self._build_settings

        super().build(build_settings)

        handlers = self.get_handler_chain()
        video_built = handlers[0].execute(self, build_settings)

        self._source = type(
            build_settings.get_ml_models_gateway()
        ).__name__  # The source of the video is used later to decide if we need to reencode the video

        return video_built

    def get_handler_chain(self) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        handlers.append(VideoBuildingHandlerGenerateFomApi())
        handlers.append(PromptByKeywordsHandler())
        handlers.append(PromptByRawUserTextHandler())
        if self.build_settings.interpolate:
            handlers.append(VideoBuildingHandlerInterpolate())
        if self._needs_reencoding:
            handlers.append(VideoBuildingHandlerReencoder())

        return handlers
