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
from pathlib import Path

import pysrt

from tests.testing_medias import (
    get_test_prompt_recording_trainboy,
    get_test_recorded_prompt_path,
)
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.prompt.subtitle_extractor import SubtitleExtractor
from vikit.video.video import Video

SAMPLE_MEDIA_FOLDER = "tests/medias/"


def create_fake_prompt_for_local_tests_moss_stones_train_boy():

    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt.subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt.subtitles
    )
    prompt.audio_recording = get_test_prompt_recording_trainboy()
    prompt.text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens
    prompt.duration = 14

    return prompt


def create_fake_prompt_tired():
    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt.subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt.subtitles
    )
    prompt.audio_recording = get_test_recorded_prompt_path()
    prompt.text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens
    prompt.duration = 103  # completely random value :)

    return prompt


test_prompt_library = {
    "moss_stones-train_boy": create_fake_prompt_for_local_tests_moss_stones_train_boy(),
    "tired": create_fake_prompt_tired(),
}


def check_output_bom(video: Video, output_dir: Path):
    """
    Check if the output files in the folder contain the BOM character

    params:
    - video: Video object
    - output_dir: Path to the output folder

    returns
    - None
    """
    # so we expect to see the following:
    # - the generated (or fake) video files
    # - the subtitle files if recorded prompt is generated
    # - the background music file
    # - the prompt audio file
    # - the transition files
    # - the first and last frame images for transitions
    # - the composite video files: one global with expected name and one for each subtitle
    # List files in the directory and check for .srt extension
    srt_files = [file for file in output_dir.iterdir() if file.suffix == ".srt"]
    if video.build_settings.prompt:
        assert len(srt_files) > 0, "No .srt files found in the output directory"

    # self.assert_exists_transitions(
    #     files, len(test_prompt.subtitles)
    # )  # one transition per subtitle
    # self.assert_exists_composite_videos(
    #     files, len(test_prompt.subtitles) + 1
    # )  # one composite per subtitle +1 for the global video
    # self.assert_exists_subtitle(files, 0)
    # self.assert_exists_generated_audio_prompt(files, 0)
    # self.assert_exists_generated_bg_music(files, 0)
    # self.assert_exists_default_bg_music(files, 0)
