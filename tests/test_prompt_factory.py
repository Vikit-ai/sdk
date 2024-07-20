import pytest
import warnings
from loguru import logger

from vikit.prompt.prompt_factory import PromptFactory
from vikit.prompt.prompt_build_settings import PromptBuildSettings


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
