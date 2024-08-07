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

import pysrt
import pytest
from loguru import logger

import tests.testing_tools as tools  # used to get a library of test prompts
from vikit.common.context_managers import WorkingFolderContext
from vikit.gateways import vikit_gateway
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)

SAMPLE_PROMPT_TEXT = """A group of ancient, moss-covered stones come to life in an abandoned forest, revealing intricate carvings
and symbols. This is additional text to make sure we generate several subtitles. """

# Below are real integration tests, not to be run all the time


class TestSubtitlesExtrators:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_subtitles_extractors.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_trainboy_moss_stones_prompt(self):
        with WorkingFolderContext():
            gw = vikit_gateway.VikitGateway()
            sub_extractor = RecordedPromptSubtitlesExtractor()
            subs: pysrt.SubRipFile = await sub_extractor.extract_subtitles_async(
                recorded_prompt_file_path=tools.test_prompt_library[
                    "moss_stones-train_boy"
                ].audio_recording,
                ml_models_gateway=gw,
            )

            assert len(subs) == 3, f"awaited 4 subs, got {len(subs)}"
            for sub in subs:
                sub = pysrt.SubRipItem(sub)
                assert sub.text is not None
                logger.debug(f"Subtitle: {sub.text}")
