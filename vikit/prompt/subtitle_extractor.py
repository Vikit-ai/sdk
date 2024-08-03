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

from loguru import logger

import vikit.common.config as config


class SubtitleExtractor:
    """
    A class to extract subtitles from a sound recording,
    merge short subtitles into longer ones, or extract them as text tokens
    """

    def merge_short_subtitles(self, subtitles, min_duration=7):
        """
        Merge subtitles which total duration is less than 7 seconds
        """
        if subtitles is None:
            raise ValueError("The subtitles are not provided")

        subs = subtitles
        assert len(subs) > 0, "No Subtitles to process from the provided recording file"
        logger.debug(f"Subs to merge {len(subs)}")

        # We  make sure that all subtitles are minimum of 7 seconds in order to be able to insert two videos inside
        index = 0
        while index < len(subs) - 1:
            secondsForSubtitle = (
                subs[index].start.hours * 60 + subs[index].start.minutes
            ) * 60 + subs[index].start.seconds
            secondsForNextSubtitle = (
                subs[index + 1].start.hours * 60 + subs[index + 1].start.minutes
            ) * 60 + subs[index + 1].start.seconds
            interspace = secondsForNextSubtitle - secondsForSubtitle

            if interspace < min_duration:
                # We need to merge the subtitles
                subs[index + 1].text = subs[index].text + " " + subs[index + 1].text
                subs[index + 1].start = subs[index].start
                del subs[index]
            else:
                index = index + 1

        logger.trace(f"Subs after merge {len(subs)}")
        return subs

    def build_subtitles_as_text_tokens(self, subtitles) -> list[str]:
        """
        Create blocks of subtitles

        Args:
            subtitles: The subtitles to process

        returns:
            list of text tokens corresponding to the subtitles in some sort
            of human readable format
        """
        texts = []
        step = 0
        text = ""

        for sub in subtitles:
            numberOfWords = len(sub.text.split(" "))
            if numberOfWords > 2:
                text = text + " " + sub.text
                step += 1
                if step % config.get_nb_subs_per_video() == 0:
                    texts.append(text)
                    text = ""

        # add the remaining text
        if text:
            texts.append(text)

        return texts
