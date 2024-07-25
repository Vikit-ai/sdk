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

import pysrt

from vikit.common.decorators import log_function_params
from vikit.prompt.text_prompt import TextPrompt


class TextPromptBuilder:
    """
    Builds a text prompt

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex
    """

    def __init__(self):
        super().__init__()
        self.prompt = TextPrompt()

    @log_function_params
    def set_prompt_text(self, text: str):
        if text is None:
            raise ValueError("The text prompt is not provided")
        self.prompt._text = text
        return self

    @log_function_params
    def set_subtitles(self, subs: list[pysrt.SubRipItem]):
        """
        set the prompt text using an LLM which extracts it from the recorded file
        """
        self.prompt._subtitles = subs

        return self

    def set_recording(self, recording_path: str):
        """
        set the recording path
        """
        self.prompt._recorded_audio_prompt_path = recording_path
        return self

    def build(self):
        return self.prompt
