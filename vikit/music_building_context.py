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


class MusicBuildingContext:
    def __init__(
        self,
        apply_background_music: bool = False,
        generate_background_music: bool = False,
        use_recorded_prompt_as_audio: bool = False,
        expected_music_length: float = None,
    ):
        """
        A context class for building music.

        params:
        apply_background_music: bool, whether to apply background music to the prompt, generate_background_music won't be considered if apply_background_music False
        generate_background_music: bool, whether to generate music taking inspiration from the prompt
        use_recorded_prompt_as_audio: bool, whether to use recorded prompt as audio
        expected_music_length: float, expected length of the music in seconds

        """
        # length in seconds, setting default to 0:

        self.use_recorded_prompt_as_audio = use_recorded_prompt_as_audio
        self.apply_background_music = apply_background_music
        self.generate_background_music = generate_background_music
        self.expected_music_length = expected_music_length
        self._generated_background_music_file = None
