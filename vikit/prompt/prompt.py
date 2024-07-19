import os
from abc import ABC
from typing import Any

import pysrt

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
    generated from an audio file, or one sent or received from an LLM.

    This class is going to be used as a base class for new type of prompts as
    they are accepted by LLM's, like an image, a video, or an embedding...
    """

    def __init__(self, duration: float = 0):
        self.text = None
        self._subtitles: list[pysrt.SubRipItem] = None
        self._subtitle_extractor = None
        self.build_settings: PromptBuildSettings = PromptBuildSettings()
        self.title = "NoTitle"
        self._extended_fields: dict[str, Any] = {}
        self._duration = duration

    @property
    def extended_fields(self) -> dict[str, Any]:
        return self._extended_fields

    @extended_fields.setter
    def extended_fields(self, value: dict[str, Any]):
        self._extended_fields = value
        if "title" in value:
            self.title = value["title"]

    @property
    def full_text(self) -> str:
        """
        Returns the full text of the prompt
        """
        if self.subtitles is None or len(self.subtitles) == 0:
            return self.text if self.text is not None else ""
        else:
            return " ".join([subtitle.text for subtitle in self.subtitles])

    def get_duration(self) -> float:
        """
        Returns the duration of the recording
        """
        if self._duration:
            return self._duration

    @property
    def subtitles(self) -> list[pysrt.SubRipItem]:
        """
        Returns the subtitles of the prompt.

        Raises:
            ValueError: If the subtitles have not been prepared yet
        """
        return self._subtitles
