from abc import ABC, abstractmethod


class Handler(ABC):

    @abstractmethod
    async def execute_async(self, object_to_transform, **kwargs):
        """
        Execute the handler asynchronously.

        Args:
            object_to_transforms: The object to transform prompt to process. It usually includes build settings
            **kwargs: Additional arguments

        Returns:
            the transformed object_to_transforms
        """
        pass
