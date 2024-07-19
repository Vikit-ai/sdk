from vikit.prompt.prompt import Prompt
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.wrappers.ffmpeg_wrapper import get_media_duration


class RecordedPrompt(Prompt):
    """
    A class to represent a prompt generated from a recorded audio file. You may want to use this class
    to generate a prompt from a recorded audio file, like a podcast or a video soundtrack (e.g. a musical video clip)
    """

    def __init__(self):
        """
        Initialize the prompt with the path to the recorded audio prompt after having converted it to mp3
        """
        self.audio_recording = None
        self._subtitle_extractor = RecordedPromptSubtitlesExtractor()

    def get_duration(self) -> float:
        """
        Returns the duration of the recording
        """
        if not self.audio_recording:
            raise ValueError("The recording is not there or generated yet")
        total_length = get_media_duration(self.audio_recording)
        self._duration = total_length

        return self._duration
