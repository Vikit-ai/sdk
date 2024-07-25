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
import unittest
import pytest
from loguru import logger

import warnings
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.common.context_managers import WorkingFolderContext

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestBackgroundMusic(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_background_music.txt", rotation="10 MB")

    @pytest.mark.integration
    def test_generate_background_music_from_empty_prompt(self):
        with WorkingFolderContext():
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )

            _ = ml_gw.generate_background_music(duration=3, prompt="")

    @pytest.mark.local_integration
    def test_generate_background_music_from_short_prompt(self):
        with pytest.raises(TypeError):
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=True
            )
            _ = ml_gw.generate_background_music(duration="a")

    @pytest.mark.integration
    def test_generate_background_music_from_prompt(self):
        with WorkingFolderContext():
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )
            music_path = ml_gw.generate_background_music(duration=3, prompt=TEST_PROMPT)
            assert music_path, "There is no background music for the video"
            assert os.path.exists(music_path), "the generated music does not exists"
