from urllib.request import urlretrieve

from vikit.video.building import video_building_handler
from vikit.video.video import Video


class VideoInterpolationHandler(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video, **kwargs)

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

        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        return super()._execute_logic(video, **kwargs)
        pass
