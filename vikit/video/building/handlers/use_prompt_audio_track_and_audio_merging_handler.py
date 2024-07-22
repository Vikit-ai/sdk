from vikit.common.handler import Handler
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class UsePromptAudioTrackAndAudioMergingHandler(Handler):

    async def execute_async(self, video):
        """
        Merge music and video  as a single media file

        Args:
            video (Video): The video to process

        Returns:
            The video including generated music
        """

        if video.build.prompt._recorded_audio_prompt_path is None:
            raise ValueError("Audio file path is required for the prompt")
        video.metadata.bg_music_applied = True
        video.metadata.is_subtitle_audio_applied = True

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.build.prompt._recorded_audio_prompt_path,
            target_file_name=video.get_file_name_by_state(),
        )

        return video