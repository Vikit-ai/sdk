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
import pytest
import warnings
from loguru import logger

from vikit.common.context_managers import WorkingFolderContext
from vikit.prompt.prompt_factory import PromptFactory
from tests.tests_medias import get_test_prompt_recording, get_test_prompt_image
from vikit.gateways import replicate_gateway as replicate_gateway
from vikit.wrappers.ffmpeg_wrapper import get_media_duration

mp3_transcription = (
    "ceci est un test rapide avec nma voix enregistrée pour faire un test"
)


class TestPrompt(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt.txt", rotation="10 MB")

    @pytest.mark.unit
    def test_generate_prompt_from_empty_prompt(self):
        with pytest.raises(ValueError):
            _ = PromptFactory(
                ml_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_text(prompt_text=None)

    @pytest.mark.unit
    def test_generate_prompt_from_empty_audio(self):
        with pytest.raises(ValueError):
            _ = PromptFactory(
                ml_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_audio_file(recorded_audio_prompt_path=None)

    @pytest.mark.integration
    def test_build_basic_audio_prompt(self):
        with WorkingFolderContext():
            """
            here we check a prompt has been created sucessfully from an mp3 recording
            """
            prompt = PromptFactory(
                ml_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_audio_file(
                recorded_audio_prompt_path=get_test_prompt_recording()
            )
            assert prompt is not None, "Prompt is None"
            assert prompt.text is not None, "Prompt text is None"
            assert (
                prompt.audio_recording is not None
            ), "Prompt sound recording path is None"
            assert (
                get_media_duration(prompt.audio_recording).__ceil__()
                == get_media_duration(get_test_prompt_recording()).__ceil__()
            ), f"length of the sound recordings  is not the same: {get_media_duration(prompt.audio_recording)} != {get_media_duration(get_test_prompt_recording())}"

    @pytest.mark.integration
    def test_build_basic_text_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt = PromptFactory(
                ml_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_text(prompt_text="This is a fake prompt")
            self.assertEqual(prompt.text, "This is a fake prompt")

    @pytest.mark.integration
    def test_build_basic_image_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt_image = get_test_prompt_image()
            prompt = PromptFactory(
                ml_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_image(prompt_image=prompt_image)

            assert prompt.image is not None
