from abc import ABC, abstractmethod
from loguru import logger

"""
We do build Prompt using chain of responsability pattern. Each handler is responsible for a specific task
and knows how to pass the Prompt to the next handler in the chain. 

We also implement the template method pattern to allow the handlers to execute their logic synchronously or asynchronously
depending on the build settings, and let you implement the actual logic in one or both of those methods.
"""


class PromptBuildingHandler(ABC):

    def __init__(self, next_handler: "PromptBuildingHandler" = None):
        self.next_handler = next_handler

    @abstractmethod
    def supports_async(self) -> bool:
        """
        Check if the handler supports async execution
        While this could have been infered using introspection,
        we prefer to make it explicit and faster

        Returns:
            bool: True if the handler supports async execution, False otherwise
        """

    async def execute_async(self, text_prompt: str, prompt_build_settings, **kwargs):
        """
        Execute the handler asynchronously if supporting it

        Args:
            Prompt (text): The text prompt to process
            **kwargs: Additional arguments

        Returns:
            A tuple made of the processed prompt, PromptBuildSettings, and any additional data that may by usefull down the
            call stack
        """
        logger.info(
            f"Running handler {type(self).__name__} on a Prompt could take some time "
        )
        logger.trace("Running handler asynchronously")
        handled_text_prompt, title, kwargs = await self._execute_logic_async(
            self,
            text_prompt=text_prompt,
            prompt_build_settings=prompt_build_settings,
            **kwargs,
        )

        if not self.next_handler:  # No more handlers to process
            return handled_text_prompt, title
        else:
            logger.info(
                f"Handler {type(self).__name__} executed successfully, passing to next handler"
            )
            return await self.next_handler.execute(
                text_prompt=handled_text_prompt,
                prompt_build_settings=prompt_build_settings,
                **kwargs,
            )

    @abstractmethod
    async def _execute_logic_async(self, text_prompt, prompt_build_settings, **kwargs):
        """
        Execute the handler asynchronously, to be imlpemented by the concrete handler
        using await and async as needed

        Args:
            prompt (Prompt): The Prompt to process
            build_settings (PromptBuildSettings): The build settings
            **kwargs: Additional arguments

        Returns:
            A tuple made of the processed prompt and any additional data that may by usefull down the
            call stack
        """
