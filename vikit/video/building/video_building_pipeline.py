from loguru import logger

from vikit.video.video_build_settings import VideoBuildSettings

from vikit.video.building.handlers.default_bg_music_and_audio_merging_handler import (
    DefaultBGMusicAndAudioMergingHandler,
)
from vikit.video.building.handlers.use_prompt_audio_track_and_audio_merging_handler import (
    UsePromptAudioTrackAndAudioMergingHandler,
)
from vikit.video.building.handlers.gen_read_aloud_prompt_and_audio_merging_handler import (
    ReadAloudPromptAudioMergingHandler,
)
from vikit.video.building.handlers.generate_music_and_merge_handler import (
    GenerateMusicAndMergeHandler,
)
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.building.handlers.interpolation_handler import (
    VideoInterpolationHandler,
)


class VideoBuildingPipeline:

    def get_handlers(self, video, build_settings: VideoBuildSettings):
        """
        Get the handlers for the video building pipeline, in the right order
        - based on the build settings (interpolation)
        - based on the video itself (reencoding)
        - background music based on the build settings (background music)
        - read aloud prompt based on the build settings (read aloud prompt)

        """
        handlers = []
        handlers.extend(self.get_handlers_from_build_settings(video, build_settings))
        handlers.extend(self.get_background_music_handlers(build_settings))
        handlers.extend(self.get_read_aloud_prompt_handlers(build_settings))
        return handlers

    def get_handlers_from_build_settings(
        self, video, build_settings: VideoBuildSettings
    ):
        """
        Get the handlers for the video building pipeline, respect the order
        (i.e. interpolation before reencoding)
        """
        handlers = []

        if build_settings.interpolate:
            handlers.append(VideoInterpolationHandler())

        if video._needs_reencoding:
            handlers.append(VideoReencodingHandler())

        return handlers

    def get_background_music_handlers(self, build_settings: VideoBuildSettings):
        """
        Get the background music handlers
        """
        handlers = []
        bg_music_text_prompt = None
        # You may use specific background music and prompt audio for the composite video
        # even if not a root composite, in case the composite is a part of a bigger video
        # and if you think it is long enough to add them
        if build_settings.music_building_context.apply_background_music:
            if build_settings.music_building_context.generate_background_music:
                if build_settings.prompt:  # use the prompt if we have one
                    if build_settings.prompt.text:
                        bg_music_text_prompt = build_settings.prompt.text
                        logger.debug(
                            f"Generating background music using prompt: {build_settings.prompt.text}"
                        )
                    else:
                        logger.debug(
                            "No prompt provided for background music generation, using composite video list  concatenated titles"
                        )
                        bg_music_text_prompt = self.generate_background_music_prompt()
                if not bg_music_text_prompt or bg_music_text_prompt == "":
                    logger.warning(
                        "No textt prompt coud be used or infered for background music generation, skipping background music generation"
                    )
                else:
                    logger.debug(
                        f"build_settings.music_building_context.expected_music_length : {build_settings.music_building_context.expected_music_length}"
                    )
                    logger.debug(f"build_settings.prompt : {build_settings.prompt}")
                    music_duration = (
                        build_settings.music_building_context.expected_music_length
                        if build_settings.music_building_context.expected_music_length
                        else build_settings.prompt.duration
                    )
                    handlers.append(
                        GenerateMusicAndMergeHandler(
                            bg_music_prompt=bg_music_text_prompt,
                            music_duration=music_duration,
                        )
                    )
            else:
                if build_settings.music_building_context.use_recorded_prompt_as_audio:
                    handlers.append(UsePromptAudioTrackAndAudioMergingHandler())
                else:
                    handlers.append(DefaultBGMusicAndAudioMergingHandler())

        return handlers

    def get_read_aloud_prompt_handlers(self, build_settings: VideoBuildSettings):
        """
        Get the read aloud prompt handlers
        """
        handlers = []
        if build_settings.include_read_aloud_prompt:
            if build_settings.prompt:
                handlers.append(
                    ReadAloudPromptAudioMergingHandler(
                        recorded_prompt=build_settings.prompt
                    )
                )
            else:
                logger.warning(
                    "No prompt audio file provided, skipping audio insertion"
                )
        return handlers
