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
