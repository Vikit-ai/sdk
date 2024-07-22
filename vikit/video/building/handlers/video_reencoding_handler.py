from loguru import logger

from vikit.common.handler import Handler
from vikit.wrappers.ffmpeg_wrapper import reencode_video


class VideoReencodingHandler(Handler):

    async def execute_async(self, video):
        """
        Process the video to reencode and normalize binaries, i.e. make it so the
        different video composing a composite have the same format

        Args:
            args: The arguments: video, build_settings

        Returns:
            CompositeVideo: The composite video

        """
        logger.debug(f"Reencoding video: {video.id}, {video.media_url}")
        if not video.media_url:
            raise ValueError(f"Video {video.id} has no media url")

        logger.debug(f"Video video.media_url : {video.media_url}")
        video.metadata.is_reencoded = True
        if video._needs_video_reencoding:
            video._media_url = await reencode_video(
                video_url=video.media_url,
                target_video_name=video.get_file_name_by_state(
                    build_settings=video.build_settings
                ),
            )
            logger.trace(f"Video reencoded: {video.id}, {video.media_url}")
        else:
            logger.warning(
                f"Video {video.id} does not need reencoding, handler should not have been called"
            )

        return video