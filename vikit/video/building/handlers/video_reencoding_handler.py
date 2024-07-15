from vikit.video_building import video_building_handler
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class VideoBuildingHandlerReencoder(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return False

    def execute_async(self, video: Video, build_settings: VideoBuildSettings):
        super().execute(video, build_settings)

        if video._needs_reencoding:
            video._video_list = process_videos(
                build_settings=build_settings,  # We take the freshly generated videos as input param
                video_list=video.video_list,
                function_to_invoke=reencode_video,
            )
            video.metadata.is_reencoded = True
