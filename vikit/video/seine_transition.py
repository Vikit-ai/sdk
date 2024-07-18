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

    def prepare_build(self, build_settings=...):
        return super().prepare_build(build_settings)

    def get_file_name_by_state(self, build_settings: VideoBuildSettings) -> str:
        """
        Get the file name of the video based on the state of the video

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            str: The file name of the video
        """
        if self.metadata.is_interpolated:
            return build_settings.get_interpolated_video_path()
        return build_settings.get_transition_video_path()

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
