import random

from vikit.common.decorators import log_function_params
from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
)


class VideoMusicBuildingHandlerGenerateFomApi(
    video_building_handler.VideoBuildingHandler
):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)
        if kwargs is not None:
            if "duration" in kwargs:
                self.music_duration = kwargs["duration"]
            else:
                raise ValueError("Duration is required")

            if "bg_music_prompt" in kwargs:
                self.additional_args["bg_music_prompt"] = kwargs["bg_music_prompt"]
            else:
                self.bg_music_prompt = kwargs["bg_music_prompt"]

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            video (Video): The video to process

        Returns:
            CompositeVideo: The composite video
        """
        await super()._execute_logic_async(video, **kwargs)
        bg_music_file = await video.build_settings.get_ml_models_gateway().generate_background_music_async(
            duration=self.music_duration,
            prompt=self.bg_music_prompt,
            target_file_name=(self._target_music_file_name),
        )
        video.background_music = bg_music_file

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=video.background_music,
            target_file_name=f"bg_music_{random.getrandbits(5)}_"
            + video.media_url.split("/")[-1],
        )
        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
