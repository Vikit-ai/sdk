from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor

from loguru import logger

"""
We do build video using chain of responsability pattern. Each handler is responsible for a specific task
and knows how to pass the video to the next handler in the chain. 

We also implement the template method pattern to allow the handlers to execute their logic synchronously or asynchronously
depending on the build settings, and let you implement the actual logic in one or both of those methods.
"""


class VideoBuildingHandler(ABC):
    # Create a new process pool executor singleton
    process_pool_executor = ProcessPoolExecutor()

    def __init__(self, next_handler: "VideoBuildingHandler" = None):
        self.next_handler = next_handler

    @abstractmethod
    def is_supporting_async_mode(self):
        """
        Check if the handler supports async execution
        While this could have been infered using introspection,
        we prefer to make it explicit and faster

        Returns:
            bool: True if the handler supports async execution, False otherwise
        """

    async def execute_async(self, video, **kwargs):
        """
        Execute the handler asynchronously if supporting it

        Args:
            video (Video): The video to process
            **kwargs: Additional arguments

        Returns:
            Video: The processed video
        """
        logger.info(
            f"Running async handler {type(self).__name__} on video {video.id}, could take somne time "
        )
        handled_video, kwargs = await self._execute_logic_async(video=video, **kwargs)

        if not self.next_handler:  # No more handlers to process
            return handled_video, kwargs
        else:
            logger.info(
                f"Handler {type(self).__name__} executed successfully, passing to next handler"
            )
            return await self.next_handler.execute(handled_video, **kwargs)

    async def execute(self, video, **kwargs):
        """
        Execute the handler synchronously

        Args:
            video (Video): The video to process
            **kwargs: Additional arguments

        Returns:
            Video: The processed video
        """
        logger.info(
            f"Running sync  handler {type(self).__name__} on video {video.id}, could take somne time "
        )
        logger.trace("Running handler synchronously")
        handled_video = self._execute_logic(video=video, **kwargs)

        if not self.next_handler:  # No more handlers to process
            return handled_video
        else:
            logger.info(
                f"Handler {type(self).__name__} executed successfully, passing to next handler"
            )

            return self.next_handler.execute(handled_video, **kwargs)

    @abstractmethod
    def _execute_logic(self, video, **kwargs):
        """
        Execute the handler asynchronously, to be called if you want to
        execute the handler asynchronously explicitly

        Args:
            video (Video): The video to process
            **kwargs: Additional arguments

        Returns:
            Video: The processed video
        """

    @abstractmethod
    async def _execute_logic_async(self, video, **kwargs):
        """
        Execute the handler logic asynchronously

        Args:
            video (Video): The video to process

        Returns:
            Video: The processed video
        """
        pass
