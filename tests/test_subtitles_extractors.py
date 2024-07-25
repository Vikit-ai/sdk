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

import unittest
import warnings

import pytest
from loguru import logger
import pysrt

from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.prompt.prompt_factory import PromptFactory
from vikit.gateways import replicate_gateway as replicate_gateway
from vikit.gateways import fake_ML_models_gateway as fake_gateway

from vikit.common.context_managers import WorkingFolderContext


SAMPLE_PROMPT_TEXT = """A group of ancient, moss-covered stones come to life in an abandoned forest, revealing intricate carvings
and symbols. This is additional text to make sure we generate serveral subtitles. """

# Below are real integration tests, not to be run all the time


class TestSubtitlesExtrators(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_subtitles_extractors.txt", rotation="10 MB")

    @pytest.mark.unit
    def test_extract_raw_subs_from_text_prompt_extractor(self):
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        assert len(subs) > 0
        for sub in subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None

    @pytest.mark.unit
    def test_extract_heuristic_human_spoken_style_subs_from_text_prompt_extractor(self):
        # We  make sure that all subtitles are minimum of 7 seconds in order to be able to insert two videos inside
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        better_subs = sub_extractor.merge_short_subtitles(subs)

        for sub in better_subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None
            assert len(sub.text.split(" ")) >= 2

    @pytest.mark.local_integration
    def test_reunion_island_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            # gw = replicate_gateway.ReplicateGateway()
            gw = fake_gateway.FakeMLModelsGateway()
            test_prompt = PromptFactory(ml_gateway=gw).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            sub_extractor = RecordedPromptSubtitlesExtractor()
            subs: pysrt.SubRipFile = sub_extractor.extract_subtitles(
                recorded_prompt_file_path=test_prompt._recorded_audio_prompt_path,
                ml_models_gateway=gw,
            )

            for sub in subs:
                # sub = pysrt.SubRipItem(sub)
                assert sub.text is not None, f"Sub.text: {sub.text}"
                assert sub.text != "", f"Sub.text: {sub.text}"

    @pytest.mark.integration
    def test_reunion_island_prompt_int(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            gw = replicate_gateway.ReplicateGateway()
            test_prompt = PromptFactory(ml_gateway=gw).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            sub_extractor = RecordedPromptSubtitlesExtractor()
            subs: pysrt.SubRipFile = sub_extractor.extract_subtitles(
                recorded_prompt_file_path=test_prompt._recorded_audio_prompt_path,
                ml_models_gateway=gw,
            )

            for sub in subs:
                # sub = pysrt.SubRipItem(sub)
                assert sub.text is not None, f"Sub.text: {sub.text}"
                assert sub.text != "", f"Sub.text: {sub.text}"
