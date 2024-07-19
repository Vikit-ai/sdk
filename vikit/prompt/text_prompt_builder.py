import pysrt

from vikit.common.decorators import log_function_params
from vikit.prompt.text_prompt import TextPrompt


class TextPromptBuilder:
    """
    Builds a text prompt

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex
    """

    def __init__(self):
        super().__init__()
        self.prompt = TextPrompt()

    def set_prompt_text(self, text: str):
        if text is None:
            raise ValueError("The text prompt is not provided")
        self.prompt.text = text
        return self

    def set_subtitles(self, subs: list[pysrt.SubRipItem]):
        """
        set the prompt text using an LLM which extracts it from the recorded file
        """
        self.prompt._subtitles = subs

        return self

    def set_recording(self, recording_path: str):
        """
        set the recording path
        """
        self.prompt.recorded_audio_prompt_path = recording_path
        return self

    def set_duration(self, duration: float):
        """
        set the duration of the prompt
        """
        self.prompt._duration = duration
        return self

    def build(self):
        return self.prompt
