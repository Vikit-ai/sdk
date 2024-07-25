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

from vikit.video.composite_video_builder_strategy import CompositeVideoBuilderStrategy
from vikit.video.composite_video_builder_strategy_local import (
    CompositeVideoBuilderStrategyLocal,
)
from vikit.video.composite_video_builder_strategy_cloud import (
    CompositeVideoBuilderStrategyCloud,
)


class CompositeVideoBuilderStrategyFactory:
    """
    Factory class to get the strategy to build a composite video
    """

    def get_local_building_strategy(self) -> CompositeVideoBuilderStrategy:
        return CompositeVideoBuilderStrategyLocal()

    def get_cloud_strategy(self) -> CompositeVideoBuilderStrategy:
        return CompositeVideoBuilderStrategyCloud()
