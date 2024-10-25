import os
from moviepy.editor import VideoFileClip
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType


class ImportedVideo(Video):
    """
    ImportedVideo is a simple way to generate a video based out of an existing video file
    """

    SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv']

    def __init__(self, video_file_path: str = None):
        """
        Initialize the video with the given video file path

        Args:
            video_file_path (str): The path to the video file

        Raises:
            ValueError: If the source media URL is not set or if the video fails validations
        """
        super().__init__()

        if video_file_path:
            if os.path.exists(video_file_path):
                self.validate_video_format(video_file_path)
                
                if self.is_valid_video_file(video_file_path):
                    self.validate_frame_rate(video_file_path)
                    self.media_url = os.path.abspath(video_file_path)
                else:
                    raise ValueError("The provided video file is not valid or is corrupt.")
            else:
                raise ValueError("The provided video file path does not exist")
        else:
            raise ValueError("The video file path should be provided")

        self._needs_video_reencoding = True
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
        return str(VideoType.IMPORTED)

    async def prepare_build_hook(self, build_settings: VideoBuildSettings):
        """
        Prepare the video build

        Args:
            build_settings (VideoBuildSettings): The build settings

        Returns:
            list: The video build order
        """
        self.build_settings = build_settings
        self.are_build_settings_prepared = True
        return self

    # Additional Validations using moviepy

    @staticmethod
    def is_valid_video_file(video_file_path):
        """
        Check if the video file is valid and not corrupt

        Args:
            video_file_path (str): The path to the video file

        Returns:
            bool: True if the video is valid, False otherwise
        """
        try:
            with VideoFileClip(video_file_path) as clip:
                return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False


    @staticmethod
    def validate_frame_rate(video_file_path, min_fps=15):
        """
        Validate that the video frame rate meets the minimum frame rate

        Args:
            video_file_path (str): The path to the video file
            min_fps (int): Minimum frames per second required

        Raises:
            ValueError: If the video frame rate is too low
        """
        with VideoFileClip(video_file_path) as clip:
            fps = clip.fps
            if fps < min_fps:
                raise ValueError(f"Video frame rate is too low: {fps} fps. Minimum is {min_fps} fps.")

    @classmethod
    def validate_video_format(cls, video_file_path):
        """
        Validate that the video format is supported

        Args:
            video_file_path (str): The path to the video file

        Raises:
            ValueError: If the video format is not supported
        """
        file_extension = video_file_path.split('.')[-1].lower()
        if file_extension not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported video format: .{file_extension}. Supported formats are: {', '.join(cls.SUPPORTED_FORMATS)}.")
