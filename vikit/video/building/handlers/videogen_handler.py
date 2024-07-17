from urllib.request import urlretrieve
from loguru import logger

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.file_tools import get_validated_path


class VideoBuildingHandlerGenerateFomApi(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs) -> Video:
        await super()._execute_logic_async(video)
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

        video_link_from_prompt = (
            await (  # Should give a link on a web storage
                video.build_settings.get_ml_models_gateway().generate_video_async(
                    prompt=video.build_settings.prompt.text
                )
            )
        )
        file_name = video.get_file_name_by_state(video.build_settings)
        path_info = get_validated_path(video_link_from_prompt)
        if path_info["type"] == "local":
            video.media_url = video_link_from_prompt
            logger.debug(
                f"Video URL already on local file system, nothing to do. Path is: {video.media_url}"
            )
        else:
            logger.debug(f"Retrieving file from remote URL :  {video_link_from_prompt}")
            video.media_url = urlretrieve(
                video_link_from_prompt,
                file_name,
            )[0]

        video.metadata.is_video_generated = True

        logger.debug(f"Video generated from prompt: {video.media_url}")
        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
