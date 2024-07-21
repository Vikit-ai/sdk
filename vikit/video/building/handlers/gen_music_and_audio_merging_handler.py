from vikit.common.handler import Handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class VideoMusicBuildingHandlerGenerateFomApi(Handler):
    def __init__(
        self,
        music_duration: float,
        bg_music_prompt: str = None,
    ):
        self.music_duration = music_duration
        self.bg_music_prompt = bg_music_prompt

    async def execute_async(self, video: Video):
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

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

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.background_music,
            target_file_name=video.get_file_name_by_state(),
        )
        return video
