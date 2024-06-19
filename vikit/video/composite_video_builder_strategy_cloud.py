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

        super().execute(composite_video=composite_video, build_settings=build_settings)
        raise NotImplementedError("Not implemented yet")
