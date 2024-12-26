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

from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

from vikit.prompt.building.handlers.prompt_by_keywords_handler import (
    PromptByKeywordsHandler,
)
from vikit.prompt.building.handlers.prompt_by_raw_usertext_handler import (
    PromptByRawUserTextHandler,
)
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class TestPromptBuildingHandlers:
    """
    Test the prompt building handlers
    """

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_keywords(self):
        prompt_handler = PromptByKeywordsHandler()
        text_prompt = str("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt,
            prompt_build_settings=PromptBuildSettings(),
            ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=True
            ),
        )
        assert prompt_built is not None, "Prompt built should not be None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_from_user_text(self):
        prompt_handler = PromptByRawUserTextHandler()
        text_prompt = str("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt,
            prompt_build_settings=PromptBuildSettings(),
            ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=True
            ),
        )
        assert prompt_built is not None, "Prompt built should not be None"
