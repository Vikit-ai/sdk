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
import warnings

import pytest
from loguru import logger

import tests.testing_tools as tools  # used to get a library of test prompts
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.imported_video import ImportedVideo
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.video import Video

TESTS_MEDIA_FOLDER = "medias/"
SMALL_VIDEO_CHAT_FILE = "chat_video_super8.mp4"


def get_cat():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    media_dir = os.path.join(dir_path, TESTS_MEDIA_FOLDER)
    return os.path.join(media_dir, SMALL_VIDEO_CHAT_FILE)


class TestVideo:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        logger.add("log_test_video.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_first_frame_as_image_path_with_non_generated_video(self):
        with pytest.raises(AssertionError):
            await PromptBasedVideo(
                prompt=tools.test_prompt_library["moss_stones-train_boy"]
            ).get_first_frame_as_image()

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_last_frame_as_image_path_with_non_generated_video(self):
        with pytest.raises(AssertionError):
            await PromptBasedVideo(
                tools.test_prompt_library["moss_stones-train_boy"]
            ).get_last_frame_as_image()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_duration(self):
        assert (
            PromptBasedVideo(
                tools.test_prompt_library["moss_stones-train_boy"]
            ).get_duration()
            == 0
        ), "Duration is not 0"

    @pytest.mark.local_integration
    @pytest.mark.core_local_integration
    @pytest.mark.asyncio
    async def test_get_first_frame_as_image_path_with_sample_video(self):
        sample_video_path = os.path.join(get_cat())
        with WorkingFolderContext():
            logger.debug(f"sample_video_path : {sample_video_path}")
            video = ImportedVideo(video_file_path=sample_video_path)
            image_path = await video.get_first_frame_as_image()

            assert image_path is not None
            assert len(image_path) > 0
            assert os.path.exists(image_path)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_last_frame_as_image_path_with_sample_video(self):
        with WorkingFolderContext():
            video = ImportedVideo(video_file_path=get_cat())
            image_path = await video.get_last_frame_as_image()

            assert image_path is not None
            assert image_path.__len__() > 0
            assert os.path.exists(image_path)

    @pytest.mark.unit
    async def test_create_single_video_mix_single_video(self):
        """
        Create a single video mix
        No Music
        """
        with pytest.raises(TypeError):
            _ = Video()
