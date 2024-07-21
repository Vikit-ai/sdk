import os

from vikit.video.video import Video
from vikit.video.video_types import VideoType
from vikit.video.building.handlers.videogen_handler import (
    VideoGenHandler,
)
from vikit.common.handler import Handler


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

        self.text = raw_text_prompt
        self._title = None
        if title:
            self._title = title
        else:
            self._title = self.get_title()
        self.metadata.title = self._title
        self._needs_video_reencoding = (
            False  # We usually don't need reencoding for raw text based videos
        )

    def __str__(self) -> str:
        return super().__str__() + os.linesep + f"text: {self.text}"

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWTEXT)

    def get_title(self):
        if self._title:
            return self._title
        else:
            # If no title existing yet (should be generated straight from an LLM)
            # then get the first and last words of the prompt
            splitted_prompt = self.text.split(" ")
            clean_title_words = [word for word in splitted_prompt if word.isalnum()]
            if len(clean_title_words) == 1:
                summarised_title = clean_title_words[0]
            else:
                summarised_title = clean_title_words[0] + "-" + clean_title_words[-1]

            # Add a unique identifier suffix to prevent several videos having the same title in a composite down the road
            self._title = summarised_title
            return self._title

    async def prepare_build_hook(self, build_settings):
        """
        Prepare the video for building

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            Video: The current instance
        """
        self.build_settings = build_settings

        return self

    def get_core_handlers(self) -> list[Handler]:
        """
         Get the handler chain of the video. Order matters here.
         At this stage, we should already have the enhanced prompt and title for this video

        Args:
             build_settings (VideoBuildSettings): The settings for building the video

         Returns:
             list: The list of handlers to use for building the video
        """
        handlers = []
        handlers.append(VideoGenHandler(video_gen_text_prompt=self.text))
        return handlers
