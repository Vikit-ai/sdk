from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
import asyncio

from loguru import logger

from vikit.video.video import Video
from vikit.common.config import singletons

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

    def execute(self, video: Video, **kwargs) -> Video:
        """
        Execute the handler synchronously or asynchronously if the handler supports it

        Args:
            video (Video): The video to process
            **kwargs: Additional arguments

        Returns:
            Video: The processed video
        """
        logger.info(
            f"Running handler {type(self).__name__} on video {video.id}, could take somne time "
        )

        if self.supports_async and video.build_settings.run_async:
            handled_video = asyncio.run(self.execute_async(video))
        else:
            if video.build_settings.use_multiprocessing:
                handled_video = singletons.get_process_executor().submit(
                    self._execute_logic, video, **kwargs
                )
            else:
                handled_video = self._execute_logic(video, **kwargs)

        if not self.next_handler:  # No more handlers to process
            return handled_video
        else:
            logger.info(
                f"Handler {type(self).__name__} executed successfully, passing to next handler"
            )

            return self.next_handler.execute(handled_video, **kwargs)

    async def execute_async(self, video: Video, **kwargs):
        """
        Execute the handler asynchronously, to be called if you want to
        execute the handler asynchronously explicitly

        Args:
            video (Video): The video to process
            **kwargs: Additional arguments

        Returns:
            Video: The processed video
        """
        await self._execute_logic_async(video)

    @abstractmethod
    def _execute_logic_async(self, video: Video, **kwargs) -> Video:
        """
        Execute the handler logic asynchronously

        Args:
            video (Video): The video to process

        Returns:
            Video: The processed video
        """
        pass

    @abstractmethod
    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Execute the handler logic

        Args:
            video (Video): The video to process

        Returns:
            Video: The processed video
        """
        pass
