from vikit.prompt.prompt import Prompt
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.wrappers.ffmpeg_wrapper import get_media_duration


class TextPrompt(Prompt):
    """
    A class to represent a text prompt
    """

    def __init__(self, prompt_text: str = None):
        super().__init__()
        # yes for now a TextPrompt can have a recordedAudioprompt path
        # which might have been generated from an LLM so we can extract subtitles with some
        # fidelity to a human like reader that reads the prompt.
        self._recorded_audio_prompt_path = None
        self._text = prompt_text
        self._subtitle_extractor = TextPromptSubtitlesExtractor()

    def get_duration(self) -> float:
        """
        Returns the duration of the recording
        """
        if self._recorded_audio_prompt_path is None:
            raise ValueError("The recording is not there or generated yet")
        total_length = get_media_duration(self._recorded_audio_prompt_path)
        return total_length
