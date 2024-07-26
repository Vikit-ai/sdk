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

from loguru import logger
import pysrt

from vikit.wrappers.ffmpeg_wrapper import convert_as_mp3_file
from vikit.prompt.recorded_prompt import RecordedPrompt
import vikit.common.config as config


class RecordedPromptBuilder:
    """
    Builds a prompt based on a recorded audio file

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex

    """

    def __init__(self):
        self.prompt = RecordedPrompt()

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

        self.prompt.audio_recording = await convert_as_mp3_file(
            recorded_audio_prompt_path,
            (
                prompt_mp3_file_name
                if prompt_mp3_file_name
                else config.get_prompt_mp3_file_name()
            ),
        )

        logger.debug(f"Recorded audio prompt path {self.prompt.audio_recording}")

        return self

    def set_subtitles(self, subs: list[pysrt.SubRipItem]):
        """
        set the prompt text using an LLM which extracts it from the recorded file
        """
        self.prompt.subtitles = subs

        return self

    def set_audio_recording(self, audio_recording: bool):
        self.prompt.audio_recording = audio_recording
        return self

    def set_prompt_text(self, text: str):
        if text is None:
            raise ValueError("The text prompt is not provided")
        self.prompt.text = text
        return self

    def set_duration(self, duration: float):
        if duration is None:
            raise ValueError("The duration is not provided")
        if duration <= 0:
            raise ValueError("The duration is not valid")
        self.prompt.duration = duration

        return self

    def build(self):
        return self.prompt
