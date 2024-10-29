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

from tests.testing_medias import get_test_prompt_image, get_test_prompt_recording
from vikit.common.context_managers import WorkingFolderContext
from vikit.gateways import replicate_gateway as replicate_gateway
from vikit.gateways import vikit_gateway as vgateway
from vikit.prompt.prompt_factory import PromptFactory

mp3_transcription = "This is a quick test with my recorded voice to do a test"


class TestPrompt:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_prompt_from_empty_prompt(self):
        with pytest.raises(ValueError):
            _ = await PromptFactory(
                ml_models_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_text(prompt_text=None)

    @pytest.mark.unit
    def test_generate_prompt_from_empty_audio(self):
        # with pytest.raises(ValueError):
        _ = PromptFactory(
            ml_models_gateway=replicate_gateway.ReplicateGateway()
        ).create_prompt_from_audio_file(recorded_audio_prompt_path=None)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_basic_audio_prompt_from_existing_recording(self):
        with WorkingFolderContext():
            """
            here we check a prompt has been created successfully from an mp3 recording
            """
            prompt = await PromptFactory(
                ml_models_gateway=vgateway.VikitGateway()
            ).create_prompt_from_audio_file(
                recorded_audio_prompt_path=get_test_prompt_recording()
            )
            assert prompt is not None, "Prompt is None"
            assert prompt.text is not None, "Prompt text is None"
            assert prompt.audio_recording is not None, "Prompt recording path is None"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_basic_text_prompt_from_text(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt = await PromptFactory(
                ml_models_gateway=vgateway.VikitGateway()
            ).create_prompt_from_text(prompt_text="This is a fake prompt")
            assert (
                prompt.text == "This is a fake prompt"
            ), "Prompt text is not the one expected"

    @pytest.mark.integration
    async def test_build_basic_image_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt_image = get_test_prompt_image()
            prompt = await PromptFactory(
                ml_models_gateway=replicate_gateway.ReplicateGateway()
            ).create_prompt_from_image(image=prompt_image)

            assert prompt.image is not None
