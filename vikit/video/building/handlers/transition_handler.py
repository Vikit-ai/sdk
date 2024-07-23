import shutil
from urllib.request import urlretrieve
from loguru import logger

from vikit.common.file_tools import url_exists
from vikit.common.handler import Handler
from vikit.video.video import Video
from vikit.common.file_tools import get_path_type


class VideoBuildingHandlerTransition(Handler):

    async def execute_async(self, video: Video):
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        assert (
            video.source_video.media_url
        ), f"source video must be generated, video: {video.source_video}"
        assert (
            video.target_video.media_url
        ), f"target video must be generated, {video.target_video.media_url}, id: {video.target_video.id}"
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

        video.metadata.is_video_generated = True
        video.metadata.title = video.get_title()

        target_file_name = video.get_file_name_by_state(
            build_settings=video.build_settings
        )
        file_type = get_path_type(link_to_transition_video)["type"]
        logger.debug(f"file_type: {file_type}")
        if not file_type == "local":
            video.media_url = urlretrieve(
                target_file_name,
            )[0]
        else:
            logger.debug(f"Renaming {link_to_transition_video} to {target_file_name}")
            shutil.copyfile(link_to_transition_video, target_file_name)

        video.media_url = target_file_name

        return video
