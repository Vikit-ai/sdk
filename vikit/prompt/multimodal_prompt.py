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


class MultiModalPrompt(Prompt):
    """
    A class to represent an image prompt
    """

    def __init__(self, text: str = None, negative_text:str = None, image: str = None, audio: str = None, video:str = None, duration:float = None, seed:int=None):
        super().__init__()
        if text is None and image is None and audio is None and video is None:
            raise ValueError("No prompt data is provided")
        self.image = image
        self.text = text
        self.negative_text = negative_text
        self.audio = audio
        self.video = video
        self.duration = duration
        self.seed = seed