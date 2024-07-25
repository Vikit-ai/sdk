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

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.composite_video_builder_strategy import (
    CompositeVideoBuilderStrategy,
)


class CompositeVideoBuilderStrategyCloud(CompositeVideoBuilderStrategy):

    def execute(
        self, composite_video: "CompositeVideo", build_settings: VideoBuildSettings
    ) -> "CompositeVideo":
        """
        Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
        as we call external services and run video mixing locally.
        The video mixing process happens once we have all the videos to mix

        Args:
            composite_video: The composite video
            build_settings: The build settings

        Returns:
            root_composite_video: a built composite video
        """

        raise NotImplementedError("Not implemented yet")
