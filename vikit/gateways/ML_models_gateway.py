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

    def generate_background_music(self, duration: int = 3, prompt: str = None) -> str:
        pass

    def generate_seine_transition(self, source_image_path, target_image_path):
        pass

    def cleanse_llm_keywords(input):
        pass

    def compose_music_from_text(self, prompt_text: str, duration: int):
        pass

    def get_music_generation_keywords(self, text) -> str:
        pass

    def interpolate(self, video):
        pass

    def get_keywords_from_prompt(self, subtitleText, excluded_words: str = None):
        pass

    def get_enhanced_prompt(self, subtitleText):
        pass

    def get_subtitles(self, audiofile_path: str):
        pass

    @abstractmethod
    def generate_video(self, prompt: str):
        pass
