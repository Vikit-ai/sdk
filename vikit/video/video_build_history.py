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


class VideoBuildHistory:
    """
    Video build history: Not implemented yet, will be used pretty much like Keras model fit history
    and for instrumentation purposes
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
