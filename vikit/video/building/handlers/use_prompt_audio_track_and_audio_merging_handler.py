import random

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.decorators import log_function_params
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class UsePromptAudioTrackAndAudioMergingHandler(
    video_building_handler.VideoBuildingHandler
):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Merge music and video  as a single media file
        
        Args:
            video (Video): The video to process

        Returns:
            The video including generated music 
        """
        if video.build.prompt._recorded_audio_prompt_path is None:
            raise ValueError("Audio file path is required for the prompt")

        self.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.build.prompt._recorded_audio_prompt_path,
            target_file_name=f"audio_{random.getrandbits(16)}_"
            + video.media_url.split("/")[-1],
        )
        video.metadata.bg_music_applied = True
        video.metadata.is_subtitle_audio_applied = True

        return video, kwargs

    def _execute_logic(self, video: Video) -> Video:
        return super()._execute_logic(video)
        pass
