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


import pytest

from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.prompt.prompt_factory import PromptFactory
from tests.testing_medias import get_test_prompt_image

TEST_PROMPT = get_test_prompt_image()


class TestPromptFactory:

    @pytest.mark.local_integration
    async def test_override_model_provider(self):
        image_prompt = await PromptFactory(
            prompt_build_settings=PromptBuildSettings()
        ).create_prompt_from_image(
            image=TEST_PROMPT, text="test image prompt", model_provider="fake model"
        )
        assert (
            image_prompt.build_settings.model_provider == "fake model"
        ), "The prompt model should be overrided when model_provider is not None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text(self):

        pt_build_settings = PromptBuildSettings(
            generate_from_llm_keyword=True, generate_from_llm_prompt=False
        )
        mlgw = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
        text_prompt = await PromptFactory(
            ml_models_gateway=mlgw
        ).get_reengineered_prompt_text_from_raw_text(
            prompt="this is a test prompt", prompt_build_settings=pt_build_settings
        )
        assert isinstance(text_prompt, str), "Prompt should be a TextPrompt"
        assert text_prompt is not None, "Prompt built should not be None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text_noinputs(self):
        with pytest.raises(AttributeError):
            mlgw = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
            _ = await PromptFactory(
                ml_models_gateway=mlgw
            ).get_reengineered_prompt_text_from_raw_text(
                prompt=None, prompt_build_settings=None
            )
