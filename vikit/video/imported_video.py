import os
from vikit.video.video import Video, VideoBuildSettings
from vikit.common.decorators import log_function_params
from vikit.video.video_types import VideoType
from vikit.video.building.video_building_handler import VideoBuildingHandler


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

    @log_function_params
    async def build(self, build_settings: VideoBuildSettings = None):
        """
        Build the video

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            ImportedVideo: The built video
        """
        if self.are_build_settings_prepared:
            build_settings = self.build_settings

        await super().build(build_settings)

        return self

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.TRANSITION)

    @log_function_params
    def get_file_name_by_state(
        self,
        build_settings: VideoBuildSettings,
    ):
        """
        Get the file name of the video

        Returns:
            str: The file name of the video
        """
        return super().get_file_name_by_state(build_settings)

    @log_function_params
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

    def get_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method

        At this stage, we should already have the enhanced prompt and title for this video

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []

        return handlers
