# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from abc import ABC, abstractmethod


class MLModelsGateway(ABC):
    """
    This class is a gateway to a remote API hosting Machine Learning models as a service.
    It abstracts the main features needed to interact with the API

    Stubs inheriting from this class may be created for each model to be used so as to prevent
    dependencies on the actual API implementation and speed up tests
    """

    def __init__(self):
        pass

    async def generate_mp3_from_text_async(self, prompt_text, target_file):
        pass

    @abstractmethod
    async def generate_background_music_async(
        self, duration: int = 3, prompt: str = None, target_file_name: str = None
    ) -> str:
        pass

    @abstractmethod
    async def generate_seine_transition_async(
        self, source_image_path, target_image_path
    ):
        pass

    def cleanse_llm_keywords_async(input):
        pass

    @abstractmethod
    async def compose_music_from_text_async(self, prompt_text: str, duration: int):
        pass

    @abstractmethod
    async def get_music_generation_keywords_async(self, text) -> str:
        pass

    @abstractmethod
    async def interpolate_async(self, video):
        pass

    @abstractmethod
    async def get_keywords_from_prompt_async(
        self, subtitleText, excluded_words: str = None
    ):
        pass

    @abstractmethod
    async def get_enhanced_prompt_async(self, subtitleText):
        pass

    @abstractmethod
    async def get_subtitles_async(self, audiofile_path: str):
        pass

    @abstractmethod
    def generate_video_async(self, prompt, model_provider: str, aspect_ratio:tuple):
        pass
