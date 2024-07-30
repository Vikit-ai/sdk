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

from vikit.common.decorators import log_function_params
from vikit.prompt.image_prompt import ImagePrompt


class ImagePromptBuilder:
    """
    Builds an image prompt

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex
    """

    def __init__(self):
        super().__init__()
        self.prompt = ImagePrompt()

    @log_function_params
    def set_prompt_image(self, image: str, text: str):
        if image is None:
            raise ValueError("The image prompt is not provided")
        self.prompt._image = image
        self.prompt._text = text

        return self

    def build(self):
        return self.prompt
