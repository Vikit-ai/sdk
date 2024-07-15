from vikit.video_building import video_building_handler
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class VideoBuildingHandlerGenerateFomApi(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return True

    def execute(self, video: Video, build_settings: VideoBuildSettings):
        super().execute(video, build_settings)
        self._generate_fom_api()
