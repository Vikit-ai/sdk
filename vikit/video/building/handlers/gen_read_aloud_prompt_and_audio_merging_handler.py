from vikit.common.handler import Handler
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class ReadAloudPromptAudioMergingHandler(Handler):
    """
    Handler used to apply a synthetic voice to the video, as an audio prompt
    """

    def __init__(self, recorded_prompt):
        if not recorded_prompt:
            raise ValueError("Recorded prompt is required")
        self.recorded_prompt = recorded_prompt

    async def execute_async(self, video):
        """
        Merge prompt generated recording with video  as a single media file

        Args:
            video (Video): The video to process

        Returns:
            The video including generated synthetic voice that reads the prompt
        """
        video.metadata.is_prompt_read_aloud = True
        video.metadata.bg_music_applied = True

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=self.recorded_prompt.audio_recording,
            target_file_name=video.get_file_name_by_state(
                build_settings=video.build_settings
            ),
        )
        assert video.media_url, "Media URL was not generated properly"

        return video
