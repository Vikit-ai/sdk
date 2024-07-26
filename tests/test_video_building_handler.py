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

import warnings

import pytest
from loguru import logger

from vikit.video.building.handlers.videogen_handler import (
    VideoGenHandler,
)
from vikit.video.raw_text_based_video import RawTextBasedVideo


class TestVideoBuildingHandler:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_video_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_VideoBuildingHandlerGenerateFomApi(self):
        vid = RawTextBasedVideo(raw_text_prompt="test")
        api_handler = VideoGenHandler(video_gen_text_prompt="test")
        video_built = await api_handler.execute_async(video=vid)
        assert video_built is not None, "Video built should not be None"
        logger.debug(f"Video built media: {video_built.media_url}")
        assert video_built.media_url is not None, "Video built should have a media url"
