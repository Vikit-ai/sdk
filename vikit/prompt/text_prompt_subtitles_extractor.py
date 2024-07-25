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
from vikit.prompt.subtitle_extractor import SubtitleExtractor
import vikit.common.config as config


class TextPromptSubtitlesExtractor(SubtitleExtractor):
    """
    A class to extract subtitles from a sound recording,
    merge short subtitles into longer ones, or extract them as text tokens

    We do use an heuristic, so it is not as good
    as creating a recording and getting the prompts from LLMs in the right language
    but it is a good start and it goes faster than the other way around.

    So  here we just split the text prompt into words and consider each word takes roughly
    x seconds to pronounce. All these are set in config files

    Here we don't need to rebuild a full srt file as with recorded prompts

    """

    @log_function_params
    def extract_subtitles(self, text) -> list[pysrt.SubRipItem]:
        """
        Generate subtitles from a text prompt

        Args:
            text: The text prompt

        Returns:
            A list of subtitles generated from the text prompt as a list of pysrt.SubRipItem
        """
        assert text is not None, "The text prompt is not provided"
        words = text.split(" ")
        subs = []
        i = 0
        nb_words_per_sub = config.get_nb_words_per_subtitle()
        sec_per_word = config.get_seconds_per_word()
        while i < len(words):
            sub = pysrt.SubRipItem()
            sub.index = i
            sub.text = " ".join(words[i : i + nb_words_per_sub])
            sub.start.seconds = i * sec_per_word
            sub.end.seconds = (i + nb_words_per_sub) * sec_per_word
            subs.append(sub)
            i += config.get_nb_words_per_subtitle()
        return subs
