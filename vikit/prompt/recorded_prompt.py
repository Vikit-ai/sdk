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

from vikit.prompt.prompt import Prompt
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.wrappers.ffmpeg_wrapper import get_media_duration


class RecordedPrompt(Prompt):
    """
    A class to represent a prompt generated from a recorded audio file. You may want to use this class
    to generate a prompt from a recorded audio file, like a podcast or a video soundtrack (e.g. a musical video clip)
    """

    def __init__(self):
        """
        Initialize the prompt with the path to the recorded audio prompt after having converted it to mp3
        """
        self._recorded_audio_prompt_path = None
        self._subtitle_extractor = RecordedPromptSubtitlesExtractor()

    @property
    def audio_recording(self):
        return self._recorded_audio_prompt_path

    def get_duration(self) -> float:
        """
        Returns the duration of the recording
        """
        if self._recorded_audio_prompt_path is None:
            raise ValueError("The recording is not there or generated yet")
        total_length = get_media_duration(self._recorded_audio_prompt_path)
        return total_length
