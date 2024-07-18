from loguru import logger

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import reencode_video
from vikit.common.decorators import log_function_params


class VideoReencodingHandler(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Process the video to reencode and normalize binaries, i.e. make it so the
        different video composing a composite have the same format

        Args:
            args: The arguments: video, build_settings

        Returns:
            CompositeVideo: The composite video

        """
        logger.debug(f"Reencoding video: {video.id}, {video.media_url}")
        await super()._execute_logic_async(video, **kwargs)
        if not video.media_url:
            raise ValueError(f"Video {video.id} has no media url")

        logger.debug(f"Video video.media_url : {video.media_url}")
        if video._needs_reencoding:
            video._media_url = await reencode_video(
                video_url=video.media_url,
                target_video_name=video.get_file_name_by_state(
                    build_settings=video.build_settings
                ),
            )
        else:
            return video, kwargs

        video.metadata.is_reencoded = True

        logger.trace(f"Video reencoded: {video.id}, {video.media_url}")
        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs):
        """
        Process the video generation  synchronously
        """
        pass
