from typing import Any, Tuple

from vikit.prompt.text_prompt import TextPrompt
from vikit.prompt.building.prompt_building_handler import PromptBuildingHandler
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class PromptByKeywordsHandler(PromptBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return True

    async def _execute_logic_async(
        self, text_prompt: str, prompt_build_settings: PromptBuildSettings, **kwargs
    ):
        """
        Process the text prompt to generate a list of keywords, and a title
        summarizing those keywords

        We do some forme of "keywords decay" by passing keywords not to be used in the targer
        keyword list. Those are typically the keywords that have already been inserted
        in the prompt text, with some forgetting of the older ones

        Args:
            prompt (str): The prompt to generate the keywords from
            prompt_build_settings (VideoBuildSettings): The build settings
            **kwargs: Additional arguments

        Returns:
            an enhanced prompt to be used for video generation
        """
        step = 20  # This is a constant that is used to determine the number of words to decay so they
        # won't be included into the prompt
        await super()._execute_logic_async(text_prompt, prompt_build_settings, **kwargs)

        # if len(excluded_words) > 0:
        #     new_excluded_words = kwargs.get("excluded_words", "")
        #     for i in range(excluded_words_depth):
        #         new_excluded_words = new_excluded_words + kwargs.get(
        #             "enhanced_prompt", ""
        #         )
        # enhanced_prompt, enhanced_title = (
        #     await prompt_build_settings.get_ml_models_gateway().get_keywords_from_prompt_async(
        #         subtitleText=text_prompt,
        #         excluded_words=(kwargs.get("excluded_words", "")),
        #     ),
        # )
        return "KEYWORDS FROM PROMPT", "test title", kwargs

        # new_excluded_words = ""
        # return (
        #     enhanced_prompt,
        #     enhanced_title,
        #     prompt_build_settings,
        #     kwargs.extend(
        #         {
        #             "excluded_words": new_excluded_words,
        #         }
        #     ),
        # )
