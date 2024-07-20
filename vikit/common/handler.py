from abc import ABC, abstractmethod


class Handler(ABC):

    @abstractmethod
    async def execute_async(self, object_to_transform, settings, **kwargs):
        """
        Execute the handler asynchronously.

        Args:
            object_to_transforms: The object to transform prompt to process
            settings: The settings to use for the transformation

        Returns:
            the transformed object_to_transforms
        """
        pass
