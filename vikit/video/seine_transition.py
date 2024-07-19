from vikit.video.video import Video, VideoBuildSettings
from vikit.video.transition import Transition
from vikit.video.building.handlers.transition_handler import (
    VideoBuildingHandlerTransition,
)
from vikit.video.building.handlers.interpolation_handler import (
    VideoInterpolationHandler,
)
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.building.video_building_handler import VideoBuildingHandler


class SeineTransition(Transition):

    def __init__(
        self,
        source_video: Video,
        target_video: Video,
    ):
        """
        A Seine transition is a video that is generated between two videos
        """
        super().__init__(source_video=source_video, target_video=target_video)

    async def prepare_build(self, build_settings=...):
        return await super().prepare_build(build_settings)

    def get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method

        At this stage, we should already have the enhanced prompt and title for this video

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        handlers.append(VideoBuildingHandlerTransition())
        if build_settings.interpolate:
            handlers.append(VideoInterpolationHandler())
        if self._needs_reencoding:
            handlers.append(VideoReencodingHandler())

        return handlers
