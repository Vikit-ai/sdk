from loguru import logger
from urllib.request import urlretrieve
import asyncio

from vikit.video.video import Video, VideoBuildSettings
from vikit.common.decorators import log_function_params
from vikit.video.transition import Transition, url_exists
from vikit.video.building.video_building_handler import VideoBuildingHandler
from vikit.video.building.handlers.transition_handler import (
    VideoBuildingHandlerTransitioni,
)
from vikit.video.building.handlers.interpolation_handler import (
    VideoBuildingHandlerInterpolate,
)
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoBuildingHandlerReencoder,
)


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

    @log_function_params
    async def build(self, build_settings: VideoBuildSettings = None) -> Transition:
        """
        Apply the Seine transition between the source and target video

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            str: The path to the generated transition video
        """
        if self.are_build_settings_prepared:
            build_settings = self.build_settings

        await super().build(build_settings)

        if self.is_video_generated:
            return self

        if not self.source_video.is_video_generated:
            await self.source_video.build(build_settings=build_settings)
        if not self.target_video.is_video_generated:
            await self.target_video.build(build_settings=build_settings)

        assert self.source_video.is_video_generated, "source video must be generated"
        assert self.target_video.is_video_generated, "target video must be generated"
        assert url_exists(self.source_video.media_url), "source_video must exist"
        assert url_exists(self.target_video.media_url), "target_video must exist"

        logger.debug(
            f"Applying transition from {self.source_video.media_url} to {self.target_video.media_url}"
        )
        ml_gw = build_settings.get_ml_models_gateway()
        # We generate a transition
        link_to_transition_video = asyncio.run(
            ml_gw.generate_seine_transition_async(
                source_image_path=self.source_video.get_last_frame_as_image(),
                target_image_path=self.target_video.get_first_frame_as_image(),
            )
        )
        if link_to_transition_video is None:
            raise ValueError("No link to transition video generated")
        logger.debug(f"URL Retrieved to be interpolated {link_to_transition_video}")

        self.metadata.is_interpolated = build_settings.interpolate

        target_file_name = self.get_file_name_by_state(build_settings=build_settings)
        if build_settings.interpolate:
            interpolated_transition_link = asyncio.run(
                ml_gw.interpolate_async(link_to_transition_video)
            )
            urlretrieve(interpolated_transition_link, target_file_name)
        else:
            urlretrieve(link_to_transition_video, target_file_name)

        self.metadata.is_video_generated = True
        self._media_url = target_file_name

        return self

    def get_video_handler_chain(
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
        handlers.append(VideoBuildingHandlerTransitioni())
        if build_settings.interpolate:
            handlers.append(VideoBuildingHandlerInterpolate())
        if self._needs_reencoding:
            handlers.append(VideoBuildingHandlerReencoder())

        return handlers
