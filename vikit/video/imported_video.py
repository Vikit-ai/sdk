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

from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType


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
