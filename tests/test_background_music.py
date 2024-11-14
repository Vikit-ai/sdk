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

from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.common.context_managers import WorkingFolderContext
from vikit.gateways.vikit_gateway import VikitGateway

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestBackgroundMusic:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_background_music.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_background_music_from_empty_prompt(self):
        with WorkingFolderContext():
            ml_gw = MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )

            _ = await ml_gw.generate_background_music_async(duration=3, prompt="")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_background_music_from_prompt(self):
        with WorkingFolderContext():
            ml_gw = MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )
            music_path = await ml_gw.generate_background_music_async(
                duration=3, prompt=TEST_PROMPT
            )
            assert music_path, "There is no background music for the video"
            assert os.path.exists(music_path), "the generated music does not exists"
