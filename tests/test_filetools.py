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

import pytest

import tests.testing_medias as testing_medias
from vikit.common.file_tools import download_or_copy_file
from vikit.common.context_managers import WorkingFolderContext


class TestFileTools:
    """
    Test the file tools functions

    Includes tests of files required to be stored on public http url, non public accessible cloud storage, and local files
    """

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
