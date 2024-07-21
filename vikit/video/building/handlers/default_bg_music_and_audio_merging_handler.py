import random

from vikit.common.handler import Handler

# from vikit.video.video import Video
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import merge_audio, extract_audio_slice


class DefaultBGMusicAndAudioMergingHandler(Handler):

    async def execute_async(self, video):
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
        audio_file = await self._fit_standard_background_music(
            expected_music_duration=expected_music_duration, video=video
        )
        video.metadata.bg_music_applied = True
        video.metadata.bg_music_applied = True

        self.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=audio_file,
            target_file_name=video.get_file_name_by_state(),
        )
        assert audio_file, "Default Background music was not fit properly to video"
        video.background_music = audio_file
        assert video.media_url, "Default Background music was not merged properly"

        return video

    async def _fit_standard_background_music(
        self, video, expected_music_duration: float = None
    ):
        """
        Prepare a standard background music for the video

        Args:
            expected_music_duration (float): The expected duration of the music
            In case the audio is shorter, we will just stop playing music when it ends, no music looping for now

        """
        return await extract_audio_slice(
            start=0,
            end=expected_music_duration,
            audiofile_path=config.get_default_background_music(),
            target_file_name=f"{video.media_url[:-4].split('/')[-1]}_background_music.mp3",
        )
