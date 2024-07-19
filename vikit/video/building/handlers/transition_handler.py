import shutil
from urllib.request import urlretrieve
from loguru import logger

from vikit.video.transition import url_exists
from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.file_tools import get_path_type


class VideoBuildingHandlerTransition(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video, kwargs=kwargs)
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        await super()._execute_logic_async(video, **kwargs)

        assert video.source_video.is_video_generated, "source video must be generated"
        assert video.target_video.is_video_generated, "target video must be generated"
        assert url_exists(video.source_video.media_url), "source_video must exist"
        assert url_exists(video.target_video.media_url), "target_video must exist"

        logger.debug(
            f"Applying transition from {video.source_video.media_url} to {video.target_video.media_url}"
        )
        ml_gw = video.build_settings.get_ml_models_gateway()
        # We generate a transition
        link_to_transition_video = await ml_gw.generate_seine_transition_async(
            source_image_path=await video.source_video.get_last_frame_as_image(),
            target_image_path=await video.target_video.get_first_frame_as_image(),
        )

        if link_to_transition_video is None:
            raise ValueError("No link to transition video generated")

        target_file_name = video.get_file_name_by_state(
            build_settings=video.build_settings
        )
        logger.debug(f"target_file_name: {target_file_name}")
        file_type = get_path_type(link_to_transition_video)["type"]
        logger.debug(f"file_type: {file_type}")
        if not file_type == "local":
            video.media_url = urlretrieve(
                target_file_name,
            )[0]
        else:
            logger.debug(f"Renaming {link_to_transition_video} to {target_file_name}")
            shutil.copyfile(link_to_transition_video, target_file_name)

        video.metadata.is_video_generated = True
        video._media_url = target_file_name

        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
