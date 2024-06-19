import os
from abc import ABC

import pysrt

from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.common.decorators import log_function_params
import vikit.common.secret as secrets


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

    @log_function_params
    def __init__(self, ml_gateway: MLModelsGateway = None):
        self._text = None
        self._subtitles: list[pysrt.SubRipItem] = None
        self._subtitle_extractor = None
        if ml_gateway is None:
            self._models_gateway = MLModelsGatewayFactory().get_ml_models_gateway()

    @property
    def text(self) -> str:
        """
        Returns the text of the prompt.
        """
        return self._text

    @property
    def subtitles(self) -> list[pysrt.SubRipItem]:
        """
        Returns the subtitles of the prompt.

        Raises:
            ValueError: If the subtitles have not been prepared yet
        """
        if self._subtitles is None:
            raise ValueError("The subtitles have not been prepared yet")

        return self._subtitles

    def get_duration(self) -> float:
        """
        Returns the duration of the prompt in seconds. This is not ideal and should be used only if
        we don't have the recording of the prompt.
        """
        if self.subtitles is None:
            raise ValueError("The subtitles have not been prepared yet")
        else:
            total_length = (
                self.subtitles[-1].end.minutes * 60 + self.subtitles[-1].end.seconds
            )
            return total_length
