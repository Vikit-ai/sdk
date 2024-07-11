from abc import abstractmethod, ABC

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_build_history import VideoBuildHistory


class VideoBuilderStrategy(ABC):
    """
    video builder strategy is the base class for strategies to build composite videos or other types of videos

    This class has been created to allow the creation of different strategies to build videos without relying too much
    on the implementation details of the composite video class
    """

    @abstractmethod
    def execute(self, video, build_settings: VideoBuildSettings) -> VideoBuildHistory:
        """
        Execute the composite video builder strategy

        We need to use hints as strings to prevent circular dependencies

        Args:
            video : The video to build
            build_settings (VideoBuildSettings): The build settings

        Returns:
            VideoBuildHistory: The video build history
        """
