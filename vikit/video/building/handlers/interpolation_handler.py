from loguru import logger

from vikit.common.file_tools import download_file
from vikit.common.handler import Handler


class VideoInterpolationHandler(Handler):

    async def execute_async(self, video):

        logger.info(
            f"About to interpolate video: id: {video.id}, media: {video.media_url[:50]}"
        )
        interpolated_video = (
            await video.build_settings.get_ml_models_gateway().interpolate_async(
                video.media_url
            )
        )
        assert interpolated_video, "Interpolated video was not generated properly"
        video.metadata.is_interpolated = True

        interpolated_video_path = await download_file(
            url=interpolated_video,
            local_path=video.get_file_name_by_state(video.build_settings),
        )

        video.media_url = interpolated_video_path
        assert video.media_url, "Interpolated video was not downloaded properly"

        return video
