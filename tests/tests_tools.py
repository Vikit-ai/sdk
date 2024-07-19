import os

from vikit.prompt.recorded_prompt import RecordedPrompt
from tests.tests_medias import (
    get_test_prompt_recording_trainboy,
    get_test_recorded_prompt_path,
    get_test_prompt_recording_stones_trainboy_path,
)
from vikit.prompt.subtitle_extractor import SubtitleExtractor

import pysrt

SAMPLE_MEDIA_FOLDER = "tests/medias/"


def create_fake_prompt_for_local_tests():
    """
    Create a fake prompt for local tests
    """
    test_subs = [
        pysrt.SubRipItem(
            index=0,
            start="00:00:00,000",
            end="00:00:03,900",
            text="A group of ancient moss-covered stones come to life in an abandoned forest,",
        ),
        pysrt.SubRipItem(
            index=1,
            start="00:00:04,400",
            end="00:00:06,320",
            text="revealing intricate carvings and symbols",
        ),
        pysrt.SubRipItem(
            index=2,
            start="00:00:07,160",
            end="00:00:10,620",
            text="A young boy traveling in the train alongside Mediterranean coast,",
        ),
        pysrt.SubRipItem(
            index=3,
            start="00:00:11,240",
            end="00:00:13,000",
            text="contemplating the sea and loving it.",
        ),
    ]
    prompt = RecordedPrompt()
    prompt.audio_recording = get_test_prompt_recording_trainboy()
    prompt._subtitles = test_subs
    prompt.text = """A group of ancient moss-covered stones come to life in an abandoned forest, revealing intricate carvings and symbols
    A young boy traveling in the train alongside Mediterranean coast, contemplating the sea and loving it."""
    prompt._subtitle_as_text_tokens = [
        "A group of ancient moss-covered stones come to life in an abandoned forest,",
        "revealing intricate carvings and symbols.",
        "A young boy traveling in the train alongside Mediterranean coast,",
        "contemplating the sea and loving it.",
    ]

    return prompt


def create_fake_prompt_for_local_tests_moss_stones_train_boy():

    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt._subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt._subtitles
    )
    prompt.audio_recording = get_test_prompt_recording_stones_trainboy_path()
    prompt.text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens

    return prompt


def create_fake_prompt_trainboy():
    _sample_media_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SAMPLE_MEDIA_FOLDER,
    )
    prompt = RecordedPrompt()
    prompt._subtitles = pysrt.open(os.path.join(_sample_media_dir, "subtitles.srt"))
    subs_as_text_tokens = SubtitleExtractor().build_subtitles_as_text_tokens(
        prompt._subtitles
    )
    prompt.audio_recording = get_test_recorded_prompt_path()
    prompt.text = " ".join(subs_as_text_tokens)
    prompt._subtitle_as_text_tokens = subs_as_text_tokens

    return prompt


test_prompt_library = {
    "moss_stones-train_boy": create_fake_prompt_for_local_tests_moss_stones_train_boy(),
    "train_boy": create_fake_prompt_for_local_tests(),
    "tired": create_fake_prompt_trainboy(),
}


def check_output_bom(folder: str):
    """
    Check if the output files in the folder contain the BOM character
    """
    raise NotImplementedError("Not implemented yet")

    for file in os.listdir(folder):
        # so we expect to see the following:
        # - the generated (or fake) video files
        # - the subtitle files
        # - the background music file
        # - the prompt audio file
        # - the transition files
        # - the first and last frame images for transitions
        # - the composite video files: one global with expected name and one for each subtitle

        self.assert_exists_generated_video(
            files, len(test_prompt.subtitles) * 2
        )  # 2 generated videos per subtitle
        self.assert_exists_transitions(
            files, len(test_prompt.subtitles)
        )  # one transition per subtitle
        self.assert_exists_composite_videos(
            files, len(test_prompt.subtitles) + 1
        )  # one composite per subtitle +1 for the global video
        self.assert_exists_subtitle(files, 0)
        self.assert_exists_generated_audio_prompt(files, 0)
        self.assert_exists_generated_bg_music(files, 0)
        self.assert_exists_default_bg_music(files, 0)

        print(file)
