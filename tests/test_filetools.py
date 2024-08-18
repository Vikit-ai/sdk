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

import tests.testing_medias as testing_medias
from vikit.common.context_managers import WorkingFolderContext
from vikit.common.file_tools import (
    download_or_copy_file,
    wait_for_file_availability,
)

logger.add("log_test_Filetools.txt", rotation="10 MB")
warnings.simplefilter("ignore", category=UserWarning)
warnings.simplefilter("ignore", ResourceWarning)


class TestFileTools:

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_Download_with_local_file(
        self,
    ):
        """
        Test the download of a local file
        """

        with WorkingFolderContext():
            local_file = testing_medias.get_cat_video_path()
            downloaded_file = await download_or_copy_file(
                local_file, "downloaded_cat.mp4"
            )

            assert downloaded_file is not None
            assert downloaded_file == "downloaded_cat.mp4"
            assert downloaded_file != ""
            assert os.path.exists(downloaded_file)
            assert os.path.getsize(downloaded_file) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_video_building_handler_success(self):
        url = await wait_for_file_availability(
            url="https://www.google.com", interval_sleep_time=1, max_attempts=10
        )
        assert url == "https://www.google.com"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_video_building_handler_raising_timeout_exception(self):
        with pytest.raises(TimeoutError):
            await wait_for_file_availability("https://example.invalid", 1, 3)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_video_building_handler_immediate_success(self):
        with WorkingFolderContext():
            with open("test.txt", "w") as f:
                f.write("test")
            url = await wait_for_file_availability("file://test.txt", 1, 2)
            assert url == "file://test.txt"


# We need a more advanced test here but it requires a more complex setup with parralel threads
# and synchronization between them. We will implement it in the future.
