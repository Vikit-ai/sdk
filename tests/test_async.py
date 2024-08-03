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

from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo

warnings.simplefilter("ignore", category=ResourceWarning)
warnings.simplefilter("ignore", category=UserWarning)
logger.add("log_test_async.txt", rotation="10 MB")


class TestAsync:

    @pytest.mark.local_integration
    def test_sinc_on_async_build_single_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            built = video.build()

            assert built.media_url is not None
            assert os.path.exists(video.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            built = await video.build_async()

            assert built.media_url is not None
            assert os.path.exists(video.media_url), "The generated video does not exist"
