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

# This test suite is used to test the audio compositions that can be made on videos,
# like using background music, adding subtitles, etc.
# It does not map exactly to one single file to test

import unittest
import warnings

import pytest
from loguru import logger

from tests.tests_medias import (
    get_cat_video_path,
    get_generated_3s_forest_video_1_path,
    get_generated_3s_forest_video_2_path,
)
from vikit.video.video import VideoBuildSettings
from vikit.video.imported_video import ImportedVideo
from vikit.video.composite_video import CompositeVideo
from vikit.common.context_managers import WorkingFolderContext
from tests.tests_tools import test_prompt_library
from vikit.music_building_context import MusicBuildingContext


class TestAudioCompositions(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.sample_video_path = get_cat_video_path()
        self.prompt_loosing_faith = None
        logger.add("log_test_audio_compositions.txt", rotation="10 MB")

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    def test_insert_subtitle_audio_no_prompt(self):
        # This test should work as we fail open: if the prompt is not provided, we should not raise an error
        vid = CompositeVideo()
        vid._insert_subtitles_audio_recording(
            VideoBuildSettings(include_audio_read_subtitles=True, prompt=None)
        )

    @pytest.mark.integration
    def test_vcomp_w_bkg_music_and_prompt_based_subtitles(self):
        with WorkingFolderContext():
            video_start = ImportedVideo(get_generated_3s_forest_video_1_path())
            video_end = ImportedVideo(get_generated_3s_forest_video_2_path())
            test_video_mixer = CompositeVideo()
            final_video = test_video_mixer.append_video(video_start).append_video(
                video_end
            )
            final_video = final_video.build(
                VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True
                    ),
                    include_audio_read_subtitles=True,
                    prompt=test_prompt_library["moss_stones-train_boy"],
                    test_mode=False,
                )
            )
            assert final_video.media_url is not None
            assert final_video.background_music is not None

    @pytest.mark.integration
    def test_apply_generated_bg_sound_on_existing_gen_videos_composite(self):
        """
        Create a single video mix with 3 imported video and default bg music
        """
        with WorkingFolderContext():
            vid1 = ImportedVideo(get_generated_3s_forest_video_1_path())
            vid2 = ImportedVideo(get_generated_3s_forest_video_2_path())

            video_comp = CompositeVideo()
            video_comp.append_video(vid1).append_video(vid2)
            video_comp.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=False,
                )
            )
