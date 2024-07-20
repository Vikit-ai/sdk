import pytest

import warnings
from loguru import logger

from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.building.handlers.prompt_by_keywords_handler import (
    PromptByKeywordsHandler,
)
from vikit.prompt.building.handlers.prompt_by_raw_usertext_handler import (
    PromptByRawUserTextHandler,
)
from vikit.prompt.text_prompt import TextPrompt


class TestPromptBuildingHandlers:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_keywords(self):
        prompt_handler = PromptByKeywordsHandler()
        text_prompt = TextPrompt("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt, build_settings=PromptBuildSettings()
        )
        assert prompt_built is not None, "Prompt built should not be None"
        assert prompt_handler.supports_async, "This handler should support async"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_PromptBuildingHandler_Gen_from_user_text(self):
        prompt_handler = PromptByRawUserTextHandler()
        text_prompt = TextPrompt("test")
        prompt_built = await prompt_handler.execute_async(
            text_prompt=text_prompt, build_settings=PromptBuildSettings()
        )
        assert prompt_built is not None, "Prompt built should not be None"
        assert prompt_handler.supports_async, "This handler should support async"
