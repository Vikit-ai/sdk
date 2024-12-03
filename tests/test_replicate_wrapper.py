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

import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.common.context_managers import WorkingFolderContext
from vikit.prompt.prompt_cleaning import cleanse_llm_keywords
from vikit.prompt.prompt_factory import PromptFactory
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

SAMPLE_PROMPT_TEXT = """A group of ancient, moss-covered stones come to life in an abandoned forest, revealing intricate carvings
and symbols. This is additional text to make sure we generate several subtitles. """


class TestReplicateWrapper:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

        logger.add("log_test_replicate_wrapper.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_int_get_keywords_from_prompt(self):

        with WorkingFolderContext():
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()

            test_prompt = await PromptFactory(ml_models_gateway=ml_gw).create_prompt_from_text(
                SAMPLE_PROMPT_TEXT
            )
            keywords, title = await ml_gw.get_keywords_from_prompt_async(
                test_prompt.text, "previous_words"
            )
            assert len(keywords) > 0
            assert len(title) > 0

    @pytest.mark.unit
    def test_extract_keywords_clean_nodigits(self):
        prompt = "A group of ancient, moss-covered stones come to life in an \n 8 abandoned forest, \n  revealing intricate,, carvings and symbols"

        result = cleanse_llm_keywords(prompt)
        assert not any(
            char.isdigit() for char in result
        ), "The result should not contain any digits"

    @pytest.mark.unit
    def test_extract_keywords_clean_nodoublecomma(self):
        prompt = "A group of ancient, moss-covered stones come to life in an \n abandoned forest,, revealing intricate,, carvings and symbols"
        result = cleanse_llm_keywords(prompt)
        assert not result.__contains__(
            ",,"
        ), "The result should not contain ',,' i.e. double commas"

    @pytest.mark.unit
    def test_extract_keywords_clean_nodots(self):
        prompt = "A group of ancient, moss-covered stones come to life in .  \n an abandoned forest, revealing intricate, carvings and symbols."
        result = cleanse_llm_keywords(prompt)
        assert not result.__contains__(
            "."
        ), "The result should not contain '.' i.e. dots"

    @pytest.mark.unit
    def test_extract_keywords_clean_empty(self):
        prompt = ""
        result = cleanse_llm_keywords(prompt)
        logger.debug(f"res : {result}")
        assert result == "", "The result should be an empty string"

    @pytest.mark.unit
    def test_extract_keywords_clean_None(self):
        with pytest.raises(AttributeError):
            prompt = None
            _ = cleanse_llm_keywords(prompt)
