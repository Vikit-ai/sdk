
import pytest
import warnings
from loguru import logger

from vikit.common.context_managers import WorkingFolderContext
from vikit.prompt.prompt_factory import PromptFactory
from tests.tests_medias import get_test_prompt_recording
from vikit.gateways import replicate_gateway as replicate_gateway

mp3_transcription = "ceci est un test rapide avec nma voix enregistrée pour faire un test"


class TestPrompt():
            
    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_prompt_from_empty_prompt(self):
        with pytest.raises(ValueError):
            _ = await PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_text(prompt_text=None)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_prompt_from_empty_audio(self):
        with pytest.raises(ValueError):
            _ = await PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_audio_file(recorded_audio_prompt_path=None)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_basic_audio_prompt_integration(self):
        with WorkingFolderContext():
            """
            here we check a prompt has been created sucessfully from an mp3 recording 
            """
            prompt = await PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_audio_file(
                recorded_audio_prompt_path=get_test_prompt_recording())
            assert prompt is not None, "Prompt is None"
            assert prompt.text is not None, "Prompt text is None"
            assert prompt.audio_recording is not None, "Prompt sound recording path is None"
            assert prompt.audio_recording == get_test_prompt_recording()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_basic_text_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt = await PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_text(prompt_text="This is a fake prompt")
            assert prompt.text == "This is a fake prompt", "Prompt text is not the one expected"


