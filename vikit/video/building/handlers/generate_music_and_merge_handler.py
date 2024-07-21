from vikit.common.handler import Handler
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class GenerateMusicAndMergeHandler(Handler):
    def __init__(
        self,
        music_duration: float,
        bg_music_prompt: str = None,
    ):
        self.music_duration = music_duration
        self.bg_music_prompt = bg_music_prompt

    async def execute_async(self, video):
        """
        Generate a background music based on the prompt and merge it with the video

        Args:
            video (Video): The video to process

        Returns:
            CompositeVideo: The composite video
        """
        self.bg_music_prompt = (
            self.bg_music_prompt
            if self.bg_music_prompt
            else video.build_settings.prompt.text
        )
        bg_music_file = await video.build_settings.get_ml_models_gateway().generate_background_music_async(
            duration=self.music_duration,
            prompt=self.bg_music_prompt,
        )
        video.background_music = bg_music_file

        video.metadata.is_bg_music_generated = True
        video.metadata.bg_music_applied = True

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.background_music,
            target_file_name=video.get_file_name_by_state(),
        )
        assert (
            video.background_music is not None
        ), "Background music was not generated properly"

        return video
