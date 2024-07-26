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

from vikit.prompt.prompt import Prompt
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)


class RecordedPrompt(Prompt):
    """
    A class to represent a prompt generated from a recorded audio file. You may want to use this class
    to generate a prompt from a recorded audio file, like a podcast or a video soundtrack (e.g. a musical video clip)
    """

    def __init__(self):
        """
        Initialize the prompt with the path to the recorded audio prompt after having converted it to mp3
        """
        self.audio_recording = None
        self.subtitles: list[pysrt.SubRipItem] = None
        self._subtitle_extractor = RecordedPromptSubtitlesExtractor()
        self.duration = None

    def get_full_text(self) -> str:
        """
        Returns the full text of the prompt
        """
        if len(self.subtitles) == 0:
            return ""
        else:
            return " ".join([subtitle.text for subtitle in self.subtitles])
