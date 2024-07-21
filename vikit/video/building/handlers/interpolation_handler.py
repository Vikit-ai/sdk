from urllib.request import urlretrieve

from vikit.common.handler import Handler
from vikit.video.video import Video


class VideoInterpolationHandler(Handler):

    async def execute_async(self, video: Video):

        interpolated_video = (
            await video.build_settings.get_ml_models_gateway().interpolate_async(
                video.media_url
            )
        )
        file_name = video.get_file_name_by_state(video.build_settings)
        interpolated_video_path = urlretrieve(
            interpolated_video,
            file_name,
        )[0]
        video.media_url = interpolated_video_path
        video.metadata.is_interpolated = True

        return video
