# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from loguru import logger

from vikit.video.building.handlers.default_bg_music_and_audio_merging_handler import (
    DefaultBGMusicAndAudioMergingHandler,
)
from vikit.video.building.handlers.gen_read_aloud_prompt_and_audio_merging_handler import (
    ReadAloudPromptAudioMergingHandler,
)
from vikit.video.building.handlers.generate_music_and_merge_handler import (
    GenerateMusicAndMergeHandler,
)
from vikit.video.building.handlers.use_prompt_audio_track_and_audio_merging_handler import (
    UsePromptAudioTrackAndAudioMergingHandler,
)
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.video_build_settings import VideoBuildSettings


class VideoBuildingPipeline:

    def get_handlers(self, video, build_settings: VideoBuildSettings):
        """
        Get the handlers for the video building pipeline, in the right order
        - background music based on the build settings (background music)
        - read aloud prompt based on the build settings (read aloud prompt)

        """
        handlers = []

        # Special case here: the video used for testing should always be reencoded as coming from heterogenous sources
        #if video.build_settings.test_mode:
        video._needs_video_reencoding = True

        if video._needs_video_reencoding:
            handlers.append(VideoReencodingHandler())

        handlers.extend(
            self.get_background_music_handlers(
                build_settings=build_settings, video=video
            )
        )
        handlers.extend(self.get_read_aloud_prompt_handlers(build_settings))

        return handlers

    def get_background_music_handlers(self, build_settings: VideoBuildSettings, video):
        """
        Get the background music handlers
        """
        handlers = []
        bg_music_text_prompt = None
        music_duration = 0
        # You may use specific background music and prompt audio for the composite video
        # even if not a root composite, in case the composite is a part of a bigger video
        # and if you think it is long enough to add them
        if build_settings.music_building_context.apply_background_music:
            if (
                build_settings.prompt and build_settings.prompt.text
            ):  # use the prompt if we have one
                bg_music_text_prompt = build_settings.prompt.text
                logger.debug(
                    f"Generating background music using prompt: {build_settings.prompt.text}"
                )
            else:
                logger.debug(
                    "No prompt or prompt text provided for background music generation, using composite video list  concatenated titles"
                )
                bg_music_text_prompt = video.generate_background_music_prompt()

            if not bg_music_text_prompt or bg_music_text_prompt == "":
                logger.warning(
                    "No text prompt could be used or inferred for background music generation, using arbitrary text prompt for background music generation"
                )
                bg_music_text_prompt = "generate a nice chill electro background music"

            logger.debug(
                f"prompt text used to generate background music : {bg_music_text_prompt}"
            )
            music_duration = (
                build_settings.music_building_context.expected_music_length
                if build_settings.music_building_context.expected_music_length
                else (
                    build_settings.prompt.duration
                    if (
                        build_settings.prompt
                        and build_settings.include_read_aloud_prompt
                    )
                    else None  # We will let the handlers use the final media duration after build
                )
            )

            if build_settings.music_building_context.generate_background_music:
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
                    handlers.append(
                        DefaultBGMusicAndAudioMergingHandler(
                            music_duration=music_duration
                        )
                    )
            if len(handlers) > 0:
                logger.warning(f"bg music added  for  Video of type {type(video)}")

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
