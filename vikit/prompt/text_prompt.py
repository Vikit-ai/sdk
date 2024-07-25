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
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.wrappers.ffmpeg_wrapper import get_media_duration


class TextPrompt(Prompt):
    """
    A class to represent a text prompt
    """

    def __init__(self, prompt_text: str = None):
        super().__init__()
        # yes for now a TextPrompt can have a recordedAudioprompt path
        # which might have been generated from an LLM so we can extract subtitles with some
        # fidelity to a human like reader that reads the prompt.
        self._recorded_audio_prompt_path = None
        self._text = prompt_text
        self._subtitle_extractor = TextPromptSubtitlesExtractor()

    def get_duration(self) -> float:
        """
        Returns the duration of the recording
        """
        if self._recorded_audio_prompt_path is None:
            raise ValueError("The recording is not there or generated yet")
        total_length = get_media_duration(self._recorded_audio_prompt_path)
        return total_length
