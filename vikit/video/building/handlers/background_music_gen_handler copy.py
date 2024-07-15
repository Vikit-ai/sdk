from vikit.video_building import video_building_handler
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class VideoBuildingHandlerGenerateMusic(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return True

    async def _execute_logic_async(self, video: Video) -> Video:
        super()._execute_logic_async(video)
        """
        Generate music for the video
        
        Args:
            video (Video): The video to process

        Returns:
            The video including generated music 
        """

        return video_build

    def _execute_logic(self, video: Video) -> Video:
        return super()._execute_logic(video)
        pass
