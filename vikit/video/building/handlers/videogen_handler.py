from urllib.request import urlretrieve
from loguru import logger

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.file_tools import get_path_type


class VideoGenHandler(video_building_handler.VideoBuildingHandler):
    def __init__(self, **kwargs):
        super().__init__()
        self.video_gen_prompt_text = None
        if "video_gen_prompt_text" in kwargs:
            self.video_gen_prompt_text = kwargs["video_gen_prompt_text"]

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs):
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
        if not self.video_gen_prompt_text:
            raise ValueError("Prompt text is not set")

        video_link_from_prompt = (
            await (  # Should give a link on a web storage
                video.build_settings.get_ml_models_gateway().generate_video_async(
                    prompt=self.video_gen_prompt_text
                )
            )
        )
        file_name = video.get_file_name_by_state(video.build_settings)
        path_info = get_path_type(video_link_from_prompt)
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
