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

import os
from abc import ABC
from typing import Any

import vikit.common.secrets as secrets
from vikit.prompt.prompt_build_settings import PromptBuildSettings

os.environ["REPLICATE_API_TOKEN"] = secrets.get_replicate_api_token()
"""
A subtitle file content looks lke this:

1
00:00:00,000 --> 00:00:05,020
I am losing my interest in human beings, in the significance of their lives and their actions.

2
00:00:06,080 --> 00:00:11,880
Someone has said it is better to study one man than ten books. I want neither books nor men,
"""


class Prompt(ABC):
    """
    A class to represent a prompt, a user written prompt, a prompt
    generated from an audio file, an image prompt, or one sent or received from an LLM.

    This class is going to be used as a base class for new type of prompts as
    they are accepted by LLM's, like a video, or an embedding...
    """

    def __init__(self, build_settings: PromptBuildSettings = PromptBuildSettings()):
        self.build_settings = build_settings
        self.title = "NoTitle"
        self._extended_fields: dict[str, Any] = {}
        self.negative_prompt = None

    @property
    def extended_fields(self) -> dict[str, Any]:
        return self._extended_fields

    @extended_fields.setter
    def extended_fields(self, value: dict[str, Any]):
        self._extended_fields = value
        if "title" in value:
            self.title = value["title"]
