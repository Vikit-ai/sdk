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

from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.prompt_factory import PromptFactory


class TestPromptFactory:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text(self):

        pt_build_settings = PromptBuildSettings(
            generate_from_llm_keyword=True, generate_from_llm_prompt=False
        )

        text_prompt = await PromptFactory().get_reengineered_prompt_text_from_raw_text(
            prompt="this is a test prompt", prompt_build_settings=pt_build_settings
        )
        assert isinstance(text_prompt, str), "Prompt should be a TextPrompt"
        assert text_prompt is not None, "Prompt built should not be None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text_noinputs(self):
        with pytest.raises(AttributeError):
            _ = await PromptFactory().get_reengineered_prompt_text_from_raw_text(
                prompt=None, prompt_build_settings=None
            )
