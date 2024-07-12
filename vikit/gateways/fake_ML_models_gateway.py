import os
from pathlib import Path
from time import sleep

import tests.tests_medias as tests_medias
import vikit.common.file_tools as ft
from vikit.prompt.prompt_cleaning import cleanse_llm_keywords
from urllib.parse import urljoin
from urllib.request import pathname2url
from vikit.gateways.ML_models_gateway import MLModelsGateway

TESTS_MEDIA_FOLDER = "tests/medias/"
STUDENT_ARM_WRITING = "student_arm_writting.mp4"

_sample_media_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    TESTS_MEDIA_FOLDER,
)


class FakeMLModelsGateway(MLModelsGateway):
    """
    This class is a gateway to a remote API hosting Machine Learning models as a service.
    It abstracts the main features needed to interact with the API

    Stubs inheriting from this class may be created for each model to be used so as to prevent
    dependencies on the actual API implementation and speed up tests
    """

    def __init__(self):
        super().__init__()

    def sleep(self, sleep_time=1):
        sleep(sleep_time)  # Simulate a long process with time.sleep

    async def generate_background_music_async(
        self, duration: float = 3, prompt: str = None, sleep_time: int = 0
    ) -> str:
        self.sleep(sleep_time)

        if type(duration) is not float:
            raise TypeError("Duration must be a float")

        if duration < 0:
            raise ValueError("Duration must be a positive float")

        return tests_medias.get_sample_gen_background_music()

    async def generate_seine_transition_async(
        self, source_image_path, target_image_path, sleep_time: int = 0
    ):
        sleep(sleep_time)  # Simulate a long process with time.sleep
        return tests_medias.get_test_transition_stones_trainboy_path()  # Important:

    # the returned name should contains "transition" in the file name so we send the same video at the interpolate call
    # later on

    def cleanse_llm_keywords(self, input):
        return cleanse_llm_keywords(input)

    async def compose_music_from_text_async(
        self, prompt_text: str, duration: int, sleep_time: int = 0
    ):
        self.sleep(sleep_time)
        return tests_medias.get_sample_generated_music_path()

    async def get_music_generation_keywords_async(
        self, text, sleep_time: int = 0
    ) -> str:
        sleep(sleep_time)  # Simulate a long process with time.sleep
        return "KEYWORDS FROM MUSIC GENERATION"

    async def interpolate_async(self, link_to_video: str, sleep_time: int = 0):
        sleep(sleep_time)  # Simulate a long process with time.sleep
        local_file_path = Path(os.path.join(_sample_media_dir, STUDENT_ARM_WRITING))
        local_file_url = urljoin("file:", pathname2url(str(local_file_path)))
        return local_file_url

    async def get_keywords_from_prompt_async(
        self, subtitleText, excluded_words: str = None, sleep_time: int = 0
    ):
        sleep(sleep_time)  # Simulate a long process with time.sleep
        return "KEYWORDS FROM PROMPT", "keywords_from_prompt_file"

    async def get_enhanced_prompt_async(self, subtitleText):
        return "ENHANCED FROM PROMPT", "enhanced_from_prompt_file"

    async def get_subtitles_async(self, audiofile_path, sleep_time: int = 0):
        self.sleep(sleep_time)
        subs = None
        with open(os.path.join(_sample_media_dir, "subtitles.srt"), "r") as f:
            subs = f.read()
        return {"transcription": subs}

    async def generate_video_async(self, prompt: str = None, sleep_time: int = 0):
        self.sleep(sleep_time)

        return ft.create_non_colliding_file_name_async(
            tests_medias.get_cat_video_path()[:-4], extension="mp4"
        )

    async def extract_audio_slice_async(
        self, i, end, audiofile_path, target_file_name: str = None, sleep_time: int = 0
    ):
        self.sleep(sleep_time)

        return tests_medias.get_test_prompt_recording_trainboy()
