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

from vikit.prompt.building.handlers.prompt_by_keywords_handler import \
    PromptByKeywordsHandler
from vikit.prompt.building.handlers.prompt_by_raw_usertext_handler import \
    PromptByRawUserTextHandler
from vikit.prompt.prompt_build_settings import PromptBuildSettings

logger.add("log_test_prompt_building_handlers.txt", rotation="10 MB")
warnings.simplefilter("ignore", category=ResourceWarning)
warnings.simplefilter("ignore", category=UserWarning)


class TestPromptBuildingHandlers:

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_keywords(self):
        prompt_handler = PromptByKeywordsHandler()
        text_prompt = str("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt, prompt_build_settings=PromptBuildSettings()
        )
        assert prompt_built is not None, "Prompt built should not be None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_from_user_text(self):
        prompt_handler = PromptByRawUserTextHandler()
        text_prompt = str("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt, prompt_build_settings=PromptBuildSettings()
        )
        assert prompt_built is not None, "Prompt built should not be None"
