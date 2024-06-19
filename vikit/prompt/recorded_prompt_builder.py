import os

from loguru import logger
import pysrt

from vikit.wrappers.ffmpeg_wrapper import convert_as_mp3_file
from vikit.prompt.recorded_prompt import RecordedPrompt
import vikit.common.config as config
from vikit.common.decorators import log_function_params


class RecordedPromptBuilder:
    """
    Builds a prompt based on a recorded audio file

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex

    """

    def __init__(self):
        self.prompt = RecordedPrompt()

    @log_function_params
    def convert_recorded_audio_prompt_path(
        self, recorded_audio_prompt_path: str, prompt_mp3_file_name=None
    ):
        """
        Convert the recorded audio prompt to mp3

        Args:
            recorded_audio_prompt_path: The path to the recorded audio file
            prompt_mp3_file_name: The name of the mp3 file to save the recording as
        """

        if recorded_audio_prompt_path is None:
            raise ValueError("The path to the recorded audio file is not provided")
        assert os.path.exists(
            recorded_audio_prompt_path
        ), f"The provided target recording path does not exists/ {recorded_audio_prompt_path}"

        self.prompt._recorded_audio_prompt_path = convert_as_mp3_file(
            recorded_audio_prompt_path,
            (
                prompt_mp3_file_name
                if prompt_mp3_file_name
                else config.get_prompt_mp3_file_name()
            ),
        )

        logger.debug(
            f"Recorded audio prompt path {self.prompt._recorded_audio_prompt_path}"
        )

        return self

    @log_function_params
    def set_subtitles(self, subs: list[pysrt.SubRipItem]):
        """
        set the prompt text using an LLM which extracts it from the recorded file
        """
        self.prompt._subtitles = subs

        return self

    def set_text(self, text: str):
        """
        Set the text prompt

        Args:
            text: The text prompt
        """
        if text is None:
            raise ValueError("The text prompt is not provided")
        self.prompt._text = text
        return self

    def build(self):
        return self.prompt
