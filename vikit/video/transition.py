import os

from urllib.request import urlopen
from urllib.error import URLError
from loguru import logger

from vikit.video.video import Video
from vikit.common.decorators import log_function_params
from vikit.video.video_file_name import VideoFileName
from vikit.video.video_types import VideoType

TIMEOUT = 5  # TODO: set to global config , seconds before stopping the request to check an URL exists


def web_url_exists(url):
    """
    Check if a URL exists on the web
    """
    try:
        urlopen(url, timeout=TIMEOUT)
        return True
    except URLError:
        return False
    except ValueError:
        return False


@log_function_params
def url_exists(url: str):
    """
    Check if a URL exists somewhere on the internet or locally. To be superseded by a more
    versatile and unified library in the future.

    Args:
        url (str): The URL to check

    Returns:
        bool: True if the URL exists, False otherwise
    """
    url_exists = False
    assert url, "url cannot be None"

    if os.path.exists(url):
        url_exists = True

    if web_url_exists(url):
        url_exists = True

    return url_exists


class Transition(Video):
    """
    Base class for transitions between videos.
    """

    def __init__(
        self,
        source_video: Video,
        target_video: Video,
    ):
        """
        A transition is a video that is generated between two videos
        """
        super().__init__()
        assert source_video is not None, "source_video cannot be None"
        assert target_video is not None, "target_video cannot be None"

        self.target_video = target_video
        self.source_video = source_video
        self.video_dependencies.extend([source_video, target_video])

    def get_title(self):
        source_id = VideoFileName.from_file_name(self.source_video.media_url).unique_id
        target_id = VideoFileName.from_file_name(self.target_video.media_url).unique_id

        return str(source_id) + "-to-" + str(target_id)

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.TRANSITION)

    def generate_background_music_prompt(self):
        """
        Get the background music prompt from the source and target videos.

        returns:
            str: The background music prompt
        """
        return self.source_video.get_title() + " " + self.target_video.get_title()
