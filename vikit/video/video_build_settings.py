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
        aspect_ratio:tuple = (16,9),
    ):
        """
        VideoBuildSettings class constructor

        params:
            delete_interim_files: bool : Whether to delete the interim files generated during the video building process

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
            output_video_file_name: str : The output video file name (one is generated for you by default)
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