import os
from vikit.video.video import Video, VideoBuildSettings
from vikit.video.video_types import VideoType
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.building.handlers.interpolation_handler import (
    VideoInterpolationHandler,
)
from vikit.common.handler import Handler


class ImportedVideo(Video):
    """
    ImportedVideo is a simple way to generate a video based out of an existing video file
    """

    def __init__(self, video_file_path: str = None):
        """
        Initialize the video with the given video file path

        Args:
            video_file_path (str): The path to the video file

        Raises:
            ValueError: If the source media URL is not set
        """
        super().__init__()
        if video_file_path:
            if os.path.exists(video_file_path):
                self.media_url = os.path.abspath(video_file_path)
            else:
                raise ValueError("the provided video file path does not exists")
        else:
            raise ValueError("The video file path should be provided")

        self._needs_reencoding = True
        self.metadata.title = self.get_title()

    def get_title(self):
        """
        Returns the title of the video.
        """
        if self.media_url is None:
            return "nomedia"
        else:
            return self.media_url.split("/")[-1].split(".")[0]

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.TRANSITION)

    async def prepare_build(
        self,
        build_settings=VideoBuildSettings(),
    ):
        """
        prepare the actual video,

        Params:
            - build_settings: allow some customization

        Returns:
            The current instance
        """
        await super().prepare_build(build_settings)

        return self

    def get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[Handler]:
        """
        Get the handler chain of the video. Order matters here.

        At this stage, we should already have the enhanced prompt and title for this video
        not much to do on an imported video, maybe some resizing and normalization
        on later versions

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        if build_settings.interpolate:
            handlers.append(VideoInterpolationHandler())
        if self._needs_reencoding:
            handlers.append(VideoReencodingHandler())

        return handlers
