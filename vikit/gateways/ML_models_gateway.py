from abc import ABC, abstractmethod
from pydantic import BaseModel


class MLModelsGateway(BaseModel, ABC):
    """
    This class is a gateway to a remote API hosting Machine Learning models as a service.
    It abstracts the main features needed to interact with the API

    Stubs inheriting from this class may be created for each model to be used so as to prevent
    dependencies on the actual API implementation and speed up tests
    """

    def __init__(self):
        pass

    def generate_mp3_from_text_async(self, prompt_text, target_file):
        pass

    @abstractmethod
    def generate_background_music_async(
        self, duration: int = 3, prompt: str = None
    ) -> str:
        pass

    @abstractmethod
    def generate_seine_transition_async(self, source_image_path, target_image_path):
        pass

    def cleanse_llm_keywords_async(input):
        pass

    @abstractmethod
    def compose_music_from_text_async(self, prompt_text: str, duration: int):
        pass

    @abstractmethod
    def get_music_generation_keywords_async(self, text) -> str:
        pass

    @abstractmethod
    def interpolate_async(self, video):
        pass

    @abstractmethod
    def get_keywords_from_prompt_async(self, subtitleText, excluded_words: str = None):
        pass

    @abstractmethod
    def get_enhanced_prompt_async(self, subtitleText):
        pass

    @abstractmethod
    async def get_subtitles_async(self, audiofile_path: str):
        pass

    @abstractmethod
    def generate_video_async(self, prompt: str):
        pass
