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

from vikit.common import GeneralBuildSettings
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt import Prompt


class VideoBuildSettings(GeneralBuildSettings.GeneralBuildSettings):
    def __init__(
        self,
        delete_interim_files: bool = False,
        target_model_provider: str = None,
        expected_length: float = None,
        include_read_aloud_prompt: bool = False,
        prompt: Prompt = None,
        interpolate: bool = False,
        music_building_context: MusicBuildingContext = MusicBuildingContext(),
        cascade_build_settings: bool = False,
        target_dir_path: str = None,
        output_video_file_name: str = None,
        vikit_api_key: str = None,
        aspect_ratio: tuple = (16, 9),
        is_good_until=None,
        prompt_updater_fn=None,
        max_attempts=1,
    ):
        """
        VideoBuildSettings class constructor

        params:
            delete_interim_files: bool : Not implemented yet, Whether to delete the interim files generated during the video building process
            target_model_provider: str : The target model provider, in case you don't want to use the one defined by Vikit for each scene of the video
            Could be vikit, haiper, stabilityai, videocrafter, etc.
            expected_length:  The expected length in seconds of the video, will be used when actually building the video
            include_read_aloud_prompt:  Include a synthetic voice that reads the prompts in the final video
            prompt: Prompt : Include subtitles in the final video and fit videos to match the prompt subtitles timelines
            generate_from_image_prompt : Ask to generate the video by generating prompts from an image
            interpolate : Ask to interpolate the video
            music_building_context: MusicBuildingContext : The music building context to use when building the video
            cascade_build_settings: bool : Whether to cascade the build settings to the sub videos
            target_path: str : The target path to save the video
            target_dir_path: str : The target directory path to save the video
            vikit_api_key: str : The Vikit API key to use when building the video
            aspect_ratio: tuple : The aspect ratio of the video
            output_video_file_name: str : The output video file name (one is generated for you by default)
            is_good_until: A filter function to apply to the generated videos
            max_attempts: The maximum number of times to attempt the video generation.
                Used only in combination with the is_good_until filter function.
            prompt_updater_fn (function): A optional hook function that updates the
                video generation prompt for each attempt. If not specified, the same
                prompt is reused for every attempt. Used in combination with the
                is_good_until filter function and max_attempts.
        """

        super().__init__(
            delete_interim_files=delete_interim_files,
            target_dir_path=target_dir_path,
            target_file_name=output_video_file_name,
        )

        self.expected_length = expected_length
        self.include_read_aloud_prompt = include_read_aloud_prompt
        self.prompt = prompt
        self.music_building_context = music_building_context
        self.interpolate = interpolate
        self.target_model_provider = target_model_provider
        self.cascade_build_settings = cascade_build_settings
        self.vikit_api_key = vikit_api_key
        self.aspect_ratio = aspect_ratio
        self.is_good_until = is_good_until
        self.max_attempts = max_attempts
        self.prompt_updater_fn = prompt_updater_fn

    def __copy__(self):
        return VideoBuildSettings(
            delete_interim_files=self.delete_interim_files,
            target_model_provider=self.target_model_provider,
            expected_length=None,
            include_read_aloud_prompt=False,
            prompt=None,
            interpolate=self.interpolate,
            music_building_context=MusicBuildingContext(),
            cascade_build_settings=self.cascade_build_settings,
            target_dir_path=self.target_dir_path,
            output_video_file_name=None,
            vikit_api_key=self.vikit_api_key,
            aspect_ratio=self.aspect_ratio,
            max_attempts=self.max_attempts,
        )
