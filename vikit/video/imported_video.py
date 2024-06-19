import os

from vikit.music import MusicBuildingContext
from vikit.video.video import Video, VideoBuildSettings
from vikit.common.decorators import log_function_params


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
                self._media_url = os.path.abspath(video_file_path)
            else:
                raise ValueError("the provided video file path does not exists")
        else:
            raise ValueError("The video file path should be provided")

        self._needs_reencoding = True

    def get_title(self):
        """
        Returns the title of the video.
        """
        if self._media_url is None:
            return "nomedia"
        else:
            return self._media_url.split("/")[-1].split(".")[0]

    @log_function_params
    def build(self, build_settings: VideoBuildSettings = None):
        """
        Build the video

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            ImportedVideo: The built video
        """
        super().build(build_settings)

        if build_settings.music_building_context.apply_background_music:
            music_file = self._build_background_music(
                VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        generate_background_music=build_settings.music_building_context.generate_background_music
                    )
                )
            )

            self._apply_background_music(background_music_file=music_file)

        return self
