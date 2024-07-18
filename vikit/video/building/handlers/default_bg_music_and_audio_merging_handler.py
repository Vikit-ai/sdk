import os
import random

from vikit.common.decorators import log_function_params
from vikit.video.building import video_building_handler
from vikit.video.video import Video
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import merge_audio, extract_audio_slice


class DefaultBGMusicAndAudioMergingHandler(video_building_handler.VideoBuildingHandler):
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
        assert video.media_url is not None, "Media URL is required for the video"
        expected_music_duration = (
            video.build_settings.music_building_context.expected_music_length
        )
        audio_file = self._fit_standard_background_music(
            expected_music_duration=expected_music_duration, video=video
        )
        self.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=audio_file,
            target_file_name=f"bg_music_{random.getrandbits(5)}_"
            + video.media_url.split("/")[-1],
        )
        video.background_music = audio_file
        assert os.path.exists(audio_file), f"File {audio_file} does not exist"
        video._is_background_music_generated = True
        video.metadata.bg_music_applied = True

        return video, kwargs

    def _execute_logic(self, video: Video) -> Video:
        return super()._execute_logic(video)
        pass

    def _fit_standard_background_music(
        self, video, expected_music_duration: float = None
    ):
        """
        Prepare a standard background music for the video

        Args:
            expected_music_duration (float): The expected duration of the music
            In case the audio is shorter, we will just stop playing music when it ends, no music looping for now

        """
        return extract_audio_slice(
            start=0,
            end=expected_music_duration,
            audiofile_path=config.get_default_background_music(),
            target_file_name=f"{video.media_url[:-4].split('/')[-1]}_background_music.mp3",
        )
