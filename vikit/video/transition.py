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

from vikit.video.video import Video
from vikit.video.video_types import VideoType


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
        source_id = self.source_video.temp_id
        target_id = self.target_video.temp_id

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
