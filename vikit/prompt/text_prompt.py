from vikit.prompt.prompt import Prompt
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor


class TextPrompt(Prompt):
    """
    A class to represent a text prompt
    """

    def __init__(self, prompt_text: str = None, duration=0, **kwargs):
        super().__init__(duration=duration)
        # for now a TextPrompt can have a recordedAudioprompt path
        # which might have been generated from an LLM so we can extract subtitles with some
        # fidelity to a human like reader that reads the prompt.
        self.recorded_audio_prompt_path = None
        self.text = prompt_text
        if kwargs:
            self.extended_fields = kwargs
        self._subtitle_extractor = TextPromptSubtitlesExtractor()
