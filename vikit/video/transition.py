# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os

from urllib.request import urlopen
from urllib.error import URLError

from vikit.video.video import Video
from vikit.common.decorators import log_function_params
from vikit.video.video_build_settings import VideoBuildSettings
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
    Check if a URL exists somewhere on the internet or locally

    Args:
        url (str): The URL to check

    Returns:
        bool: True if the URL exists, False otherwise
    """
    # TODO: identify the type of URL and just run the appropriate check
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

        self._target_video = target_video
        self._source_video = source_video

    def get_title(self):
        return str(self._source_video.id)[:5] + "-to-" + str(self._target_video.id)[:5]

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

    def build(self, build_settings: VideoBuildSettings = None):
        super().build(build_settings)
