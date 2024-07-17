import pytest
import warnings
from loguru import logger

from vikit.prompt.text_prompt import TextPrompt
from vikit.prompt.prompt_factory import PromptFactory
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class TestPromptFactory:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_prompt_from_text(self):
        text_prompt = PromptFactory().create_prompt_from_text(
            prompt_text="this is a test prompt", generate_recording=False
        )
        assert isinstance(text_prompt, TextPrompt), "Prompt should be a TextPrompt"
        assert text_prompt is not None, "Prompt built should not be None"
        assert (
            text_prompt.text == "this is a test prompt"
        ), f"Prompt text should be 'test', got {text_prompt.text}"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text(self):

        build_settings = PromptBuildSettings(
            generate_from_llm_keyword=True, generate_from_llm_prompt=False
        )

        text_prompt = await PromptFactory().get_reengineered_prompt_from_text(
            prompt="this is a test prompt", prompt_build_settings=build_settings
        )
        assert isinstance(text_prompt, TextPrompt), "Prompt should be a TextPrompt"
        assert text_prompt is not None, "Prompt built should not be None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reengineer_prompt_from_text_noinputs(self):
        _ = PromptFactory().get_reengineered_prompt_from_text(
            prompt=None, prompt_build_settings=None
        )
