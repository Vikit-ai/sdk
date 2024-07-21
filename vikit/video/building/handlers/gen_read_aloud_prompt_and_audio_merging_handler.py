import os

from vikit.common.handler import Handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class ReadAloudPromptAudioMergingHandler(Handler):
    """
    Handler used to apply a synthetic voice to the video, as an audio prompt
    """

    async def execute_async(self, video: Video):
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

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.build_settings.prompt.audio_recording,
            target_file_name="background_music_" + video.media_url.split("/")[-1],
        )
        video.metadata.is_prompt_read_aloud = True

        return video
