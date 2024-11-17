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

from vikit.prompt.prompt import Prompt
from vikit.prompt.prompt_build_settings import PromptBuildSettings
import copy


class MultiModalPrompt(Prompt):
    """
    A class to represent an multimodal prompt
    """

    def __init__(self, text: str = None, negative_text:str = None, image: str = None, audio: str = None, video:str = None, duration:float = None, seed:int=None, model_provider: str=None, reengineer_text_prompt_from_image_and_text = False, build_settings: PromptBuildSettings = PromptBuildSettings()):
        
        if model_provider is None:
            super().__init__(build_settings = build_settings)    
        else:
            new_build_settings = copy.deepcopy(build_settings)
            new_build_settings.model_provider = model_provider
            super().__init__(new_build_settings)
        if text is None and image is None and audio is None and video is None:
            raise ValueError("No prompt data is provided")
        self.image = image
        self.text = text
        self.negative_text = negative_text
        self.audio = audio
        self.video = video
        self.duration = duration
        self.seed = seed
        self.reengineer_text_prompt_from_image_and_text = reengineer_text_prompt_from_image_and_text