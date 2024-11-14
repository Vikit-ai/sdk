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
import os

import pysrt
from loguru import logger

import vikit.common.config as config
from vikit.prompt.prompt import Prompt
from vikit.wrappers.ffmpeg_wrapper import convert_as_mp3_file

from vikit.prompt.prompt_build_settings import PromptBuildSettings


class RecordedPrompt(Prompt):
    """
    A class to represent a prompt generated from a recorded audio file. You may want to use this class
    to generate a prompt from a recorded audio file, like a podcast or a video soundtrack (e.g. a musical video clip)
    """

    def __init__(self, audio_recording=None, subtitles=None, duration=None, text=None, build_settings: PromptBuildSettings = PromptBuildSettings()):
        """
        Initialize the prompt with the path to the recorded audio prompt
        """
        super().__init__(build_settings = build_settings)
        
        self.audio_recording = audio_recording
        self.subtitles: list[pysrt.SubRipItem] = subtitles
        self.duration = duration
        self.text = text

    def get_full_text(self) -> str:
        """
        Returns the full text of the prompt
        """
        if len(self.subtitles) == 0:
            return ""
        else:
            return " ".join([subtitle.text for subtitle in self.subtitles])

    async def convert_recorded_audio_prompt_path_to_mp3(
        self, recorded_audio_prompt_path: str, prompt_mp3_file_name=None
    ):
        """
        Convert the recorded audio prompt to mp3

        Args:
            recorded_audio_prompt_path: The path to the recorded audio file
            prompt_mp3_file_name: The name of the mp3 file to save the recording as
        """

        if recorded_audio_prompt_path is None:
            raise ValueError("The path to the recorded audio file is not provided")
        assert os.path.exists(
            recorded_audio_prompt_path
        ), f"The provided target recording path does not exists/ {recorded_audio_prompt_path}"

        self.audio_recording = await convert_as_mp3_file(
            recorded_audio_prompt_path,
            (
                prompt_mp3_file_name
                if prompt_mp3_file_name
                else config.get_prompt_mp3_file_name()
            ),
        )

        logger.debug(f"Recorded audio prompt path {self.audio_recording}")

        return self
