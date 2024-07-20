from loguru import logger

from vikit.common.handler import Handler
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class PromptByKeywordsHandler(Handler):

    async def execute_async(
        self,
        text_prompt: str,
        prompt_build_settings: PromptBuildSettings,
    ):
        """
        Process the text prompt to generate a better one more suited to generate a video,  and a title
        summarizing the prompt.

        Note: the excluded words feature is not used even if supported by the gateway,
        this may be activated back in the future if it is found to be useful for the
        overall video direction

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
        ) = await prompt_build_settings.get_ml_models_gateway().get_keywords_from_prompt_async(
            subtitleText=text_prompt,
        )
        logger.info(
            f"Finished processing prompt, Enhanced prompt: {enhanced_prompt}, title: {title}"
        )
        return enhanced_prompt, title
