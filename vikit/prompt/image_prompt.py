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


class ImagePrompt(Prompt):
    """
    A class to represent an image prompt
    """

    def __init__(self, prompt_image: str = None, text: str = None):
        super().__init__()
        self._image = prompt_image
        self._text = text
        self._duration = 3.9

    @property
    def image(self) -> str:
        """
        Returns the image of the prompt.
        """
        return self._image

    @property
    def text(self) -> str:
        """
        Returns the text of the prompt.
        """
        return self._text

    @property
    def duration(self) -> float:
        """
        Returns the text of the prompt.
        """
        return self._duration
