from typing import Any, Tuple

from vikit.prompt.building.prompt_building_handler import PromptBuildingHandler
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.text_prompt import TextPrompt


class PromptByRawUserTextHandler(PromptBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return True

    async def _execute_logic_async(
        self, prompt: TextPrompt, build_settings: PromptBuildSettings, **kwargs
    ) -> Tuple[TextPrompt, dict[str, Any]]:
        await super()._execute_logic_async(
            prompt, build_settings=build_settings, **kwargs
        )
        """
        Process the text prompt to generate a better one more suited to generate a video,  and a title
        summarizing the prompt.

        Args:
            prompt (str): The prompt to generate the keywords from
            build_settings (VideoBuildSettings): The build settings
            **kwargs: Additional arguments

        Returns:
            an list of keywords to be used for video generation
        """
        await super()._execute_logic_async(
            prompt, build_settings=build_settings, **kwargs
        )
        (
            enhanced_prompt,
            enhanced_title,
        ) = await build_settings.get_ml_models_gateway().get_enhanced_prompt_async(
            prompt.text
        )
        return enhanced_prompt, {"title": enhanced_title}

    def _execute_logic(
        self, prompt: TextPrompt, build_settings: PromptBuildSettings, **kwargs
    ) -> dict[str, Any]:
        super()._execute_logic_async(prompt)
        """
        Process the text prompt to generate a list of keywords, and a title
        summarizing those keywords

        We do some forme of "keywords decay" by passing keywords not to be used in the targer
        keyword list. Those are typically the keywords that have already been inserted 
        in the prompt text, with some forgetting of the older ones

        Args:
            prompt (str): The prompt to generate the keywords from
            build_settings (VideoBuildSettings): The build settings
            **kwargs: Additional arguments

        Returns:
            an list of keywords to be used for video generation
        """
        super()._execute_logic_async(prompt, **kwargs)
        (
            enhanced_prompt,
            enhanced_title,
        ) = build_settings.get_ml_models_gateway().get_enhanced_prompt_async(self._text)
        return enhanced_prompt, enhanced_title
