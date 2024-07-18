import os

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class ReadAloudPromptAudioMergingHandler(video_building_handler.VideoBuildingHandler):
    """
    Handler used to apply a synthetic voice to the video, as an audio prompt
    """

    def __init__(self, **kwargs):
        super().__init__()

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Merge music and video  as a single media file
        
        Args:
            video (Video): The video to process

        Returns:
            The video including generated music 
        """
        assert os.path.exists(
            video.background_music
        ), f"File {video.background_music} does not exist"

        self.media_url = await merge_audio(
            media_url=self.media_url,
            audio_file_path=self._background_music_file_name,
            target_file_name="background_music_" + self.media_url.split("/")[-1],
        )
        video.metadata.is_prompt_read_aloud = True

        return video, kwargs

    def _execute_logic(self, video: Video) -> Video:
        return super()._execute_logic(video)
        pass
