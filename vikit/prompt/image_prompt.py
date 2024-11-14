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


class ImagePrompt(Prompt):
    """
    A class to represent an image prompt
    """

    def __init__(self, prompt_image: str = None, text: str = None, build_settings: PromptBuildSettings = PromptBuildSettings()):
        super().__init__(build_settings = build_settings)
        if prompt_image is None:
            raise ValueError("The image prompt is not provided")
        self.image = prompt_image
        self.text = text

    @property
    def duration(self) -> float:
        """
        Returns the duration of the prompt.
        Today we just hardcode the unique image to video provider output video length
        This is clearly going to change in the next version
        """
        return 4.04
