import os
import random

from vikit.common.decorators import log_function_params
from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class BGMusicMergingHandler(video_building_handler.VideoBuildingHandler):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Merge background music and video  as a single media file
        
        Args:
            video (Video): The video to process

        Returns:
            The video including bg music 
        """
        assert os.path.exists(
            video.background_music
        ), f"File {video.background_music} does not exist"

        self.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.background_music,
            target_file_name=f"bg_music_{random.getrandbits(5)}_"
            + video.media_url.split("/")[-1],
        )
        video._is_background_music_generated = True
        video.metadata.bg_music_applied = True

        return video, kwargs

    def _execute_logic(self, video: Video) -> Video:
        return super()._execute_logic(video)
        pass
