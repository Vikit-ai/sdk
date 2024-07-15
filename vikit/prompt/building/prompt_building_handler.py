from abc import ABC, abstractmethod
import asyncio

from loguru import logger

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.prompt.prompt import Prompt

"""
We do build Prompt using chain of responsability pattern. Each handler is responsible for a specific task
and knows how to pass the Prompt to the next handler in the chain. 

We also implement the template method pattern to allow the handlers to execute their logic synchronously or asynchronously
depending on the build settings, and let you implement the actual logic in one or both of those methods.
"""


class PromptBuildingHandler(ABC):

    def __init__(self, next_handler: "PromptBuildingHandler" = None):
        self.supports_async = None
        self.next_handler = next_handler

    @abstractmethod
    def supports_async(self):
        """
        Check if the handler supports async execution
        While this could have been infered using introspection,
        we prefer to make it explicit and faster

        Returns:
            bool: True if the handler supports async execution, False otherwise
        """

    def execute(
        self, Prompt: Prompt, build_settings: VideoBuildSettings, **kwargs
    ) -> Prompt:
        """
        Execute the handler synchronously or asynchronously if the handler supports it

        Args:
            Prompt (Prompt): The Prompt to process
            **kwargs: Additional arguments

        Returns:
            Prompt: The processed Prompt
        """
        logger.info(
            f"Running handler {type(self).__name__} on Prompt {Prompt.id}, could take somne time "
        )

        if self.supports_async and Prompt.build_settings.run_async:
            handled_Prompt = asyncio.run(self.execute_async(Prompt))
        else:
            handled_Prompt = self._execute_logic(Prompt, build_settings, **kwargs)

        if not self.next_handler:  # No more handlers to process
            return handled_Prompt
        else:
            logger.info(
                f"Handler {type(self).__name__} executed successfully, passing to next handler"
            )

            return self.next_handler.execute(handled_Prompt, build_settings, **kwargs)

    async def execute_async(
        self, Prompt: Prompt, build_settings: VideoBuildSettings, **kwargs
    ):
        """
        Execute the handler asynchronously, to be called if you want to
        execute the handler asynchronously explicitly

        Args:
            Prompt (Prompt): The Prompt to process
            **kwargs: Additional arguments

        Returns:
            Prompt: The processed Prompt
        """
        await self._execute_logic_async(Prompt, build_settings, **kwargs)

    @abstractmethod
    def _execute_logic_async(self, Prompt: Prompt, **kwargs) -> Prompt:
        """
        Execute the handler logic asynchronously

        Args:
            Prompt (Prompt): The Prompt to process

        Returns:
            Prompt: The processed Prompt
        """
        pass

    @abstractmethod
    def _execute_logic(self, Prompt: Prompt, **kwargs) -> Prompt:
        """
        Execute the handler logic

        Args:
            Prompt (Prompt): The Prompt to process

        Returns:
            Prompt: The processed Prompt
        """
        pass
