# from urllib.request import urlretrieve
from vikit.common.file_tools import download_file
from vikit.common.handler import Handler


class VideoInterpolationHandler(Handler):

    async def execute_async(self, video):

        interpolated_video = (
            await video.build_settings.get_ml_models_gateway().interpolate_async(
                video.media_url
            )
        )
        video.metadata.is_interpolated = True

        interpolated_video_path = await download_file(
            url=interpolated_video,
            local_path=video.get_file_name_by_state(video.build_settings),
        )
        # interpolated_video_path = urlretrieve(
        #     interpolated_video,
        #     video.get_file_name_by_state(video.build_settings),
        # )[0]

        video.media_url = interpolated_video_path
        assert video.media_url, "Interpolated video was not generated properly"

        return video
