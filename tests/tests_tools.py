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

from vikit.prompt.recorded_prompt import RecordedPrompt
from tests.tests_medias import (
    get_test_prompt_recording_trainboy,
    get_test_recorded_prompt_path,
    get_test_prompt_recording_stones_trainboy_path,
)
from vikit.prompt.subtitle_extractor import SubtitleExtractor

import pysrt

SAMPLE_MEDIA_FOLDER = "tests/medias/"


def create_fake_prompt_for_local_tests():
    """
    Create a fake prompt for local tests
    """
    test_subs = [
        pysrt.SubRipItem(
            index=0,
            start="00:00:00,000",
            end="00:00:03,900",
            text="A group of ancient moss-covered stones come to life in an abandoned forest,",
        ),
        pysrt.SubRipItem(
            index=1,
            start="00:00:04,400",
            end="00:00:06,320",
            text="revealing intricate carvings and symbols",
        ),
        pysrt.SubRipItem(
            index=2,
            start="00:00:07,160",
            end="00:00:10,620",
            text="A young boy traveling in the train alongside Mediterranean coast,",
        ),
        pysrt.SubRipItem(
            index=3,
            start="00:00:11,240",
            end="00:00:13,000",
            text="contemplating the sea and loving it.",
        ),
    ]
    prompt = RecordedPrompt()
    prompt._recorded_audio_prompt_path = get_test_prompt_recording_trainboy()
    prompt._subtitles = test_subs
    prompt._text = """A group of ancient moss-covered stones come to life in an abandoned forest, revealing intricate carvings and symbols
    A young boy traveling in the train alongside Mediterranean coast, contemplating the sea and loving it."""
    prompt._subtitle_as_text_tokens = [
        "A group of ancient moss-covered stones come to life in an abandoned forest,",
        "revealing intricate carvings and symbols.",
        "A young boy traveling in the train alongside Mediterranean coast,",
        "contemplating the sea and loving it.",
    ]

    return prompt


def create_fake_prompt_for_local_tests_moss_stones_train_boy():

    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt._subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt._subtitles
    )
    prompt._recorded_audio_prompt_path = (
        get_test_prompt_recording_stones_trainboy_path()
    )
    prompt._text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens

    return prompt


def create_fake_prompt_tired():
    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt._subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt._subtitles
    )
    prompt._recorded_audio_prompt_path = get_test_recorded_prompt_path()
    prompt._text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens

    return prompt


test_prompt_library = {
    "moss_stones-train_boy": create_fake_prompt_for_local_tests_moss_stones_train_boy(),
    "train_boy": create_fake_prompt_for_local_tests(),
    "tired": create_fake_prompt_tired(),
}
