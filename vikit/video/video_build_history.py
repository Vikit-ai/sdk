from vikit.video import Video
from vikit.video.video_metadata import VideoMetadata
from vikit.video.video_build_settings import video_build_settings


class VideoBuildHistory:
    """
    Video build history
    """

    def __init__(self, video: Video = None):
        """
        Constructor
        """
        self._video = video
        self.generation_time = None
        self.child_videos_generation_time = None

    @property
    def video(self):
        return self._video
