from loguru import logger

from vikit.common.handler import Handler
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class PromptByRawUserTextHandler(Handler):

    async def execute_async(
        self,
        text_prompt: str,
        prompt_build_settings: PromptBuildSettings,
    ):
        """
        Process the text prompt to generate a better one more suited to generate a video,  and a title
        summarizing the prompt.

        Args:
            prompt (str): The prompt to generate the keywords from
            build_settings (PromptBuildSettings): The build settings

        Returns:
            a string containing a list of keywords to be used for video generation
        """
        logger.info(f"Processing prompt: {text_prompt}")
        (
            enhanced_prompt,
            title,
        ) = await prompt_build_settings.get_ml_models_gateway().get_enhanced_prompt_async(
            text_prompt
        )
        logger.info(
            f"Finished processing prompt, Enhanced prompt: {enhanced_prompt}, title: {title}"
        )
        return enhanced_prompt, title
