from urllib.request import urlretrieve
from loguru import logger

from vikit.common.decorators import log_function_params
from vikit.video.transition import url_exists
from vikit.video.building import video_building_handler
from vikit.video.video import Video


class VideoBuildingHandlerTransition(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, transition_video: Video, **kwargs):
        await super()._execute_logic_async(transition_video, kwargs=kwargs)
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        await super()._execute_logic_async(transition_video, **kwargs)

        assert (
            transition_video.source_video.is_video_generated
        ), "source video must be generated"
        assert (
            transition_video.target_video.is_video_generated
        ), "target video must be generated"
        assert url_exists(
            transition_video.source_video.media_url
        ), "source_video must exist"
        assert url_exists(
            transition_video.target_video.media_url
        ), "target_video must exist"

        logger.debug(
            f"Applying transition from {self.source_video.media_url} to {self.target_video.media_url}"
        )
        ml_gw = transition_video.build_settings.get_ml_models_gateway()
        # We generate a transition
        link_to_transition_video = await ml_gw.generate_seine_transition_async(
            source_image_path=await self.source_video.get_last_frame_as_image(),
            target_image_path=await self.target_video.get_first_frame_as_image(),
        )

        if link_to_transition_video is None:
            raise ValueError("No link to transition video generated")

        target_file_name = transition_video.get_file_name_by_state(
            build_settings=transition_video.build_settings
        )
        transition_video.media_url = urlretrieve(
            link_to_transition_video,
            (
                transition_video.build_settings.target_file_name
                if transition_video.build_settings.target_file_name
                else target_file_name
            ),
        )[0]

        transition_video.metadata.is_video_generated = True
        transition_video._media_url = target_file_name

        return transition_video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
