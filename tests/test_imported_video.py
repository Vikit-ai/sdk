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

import unittest
import os

# from unittest.mock import patch, MagicMock, Mock
import warnings

import pytest
from loguru import logger

from tests.tests_medias import get_cat_video_path
from vikit.video.video import VideoBuildSettings
from vikit.music_building_context import MusicBuildingContext
from vikit.video.imported_video import ImportedVideo
from vikit.common.context_managers import WorkingFolderContext


class TestImportedVideo(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_imported_video.txt", rotation="10 MB")

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.sample_video_path = get_cat_video_path()

    @pytest.mark.local_integration
    def test_apply_default_bg_sound_on_existing_video(self):
        with WorkingFolderContext():
            logger.debug(f"self.sample_video_path {self.sample_video_path}")
            vid = ImportedVideo(self.sample_video_path)
            logger.debug(f"pbv.media_url : {vid.media_url}")
            assert vid.media_url, "We should have a media_url set"
            # here we expect the default background music to be sliced and used
            vid_result = vid.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    )
                )
            )

            assert vid_result, "The video mixing should have worked"
            assert (
                vid_result.background_music
            ), "The video should have a background music"
            assert os.path.exists(
                vid_result._background_music_file_name
            ), "The background music file should exist"
            assert os.path.exists(vid_result.media_url)
