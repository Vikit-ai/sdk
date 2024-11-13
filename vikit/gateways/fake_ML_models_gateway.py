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

import asyncio
import os
import shutil
from pathlib import Path
from time import sleep
from urllib.parse import urljoin
from urllib.request import pathname2url

from loguru import logger

import tests.testing_medias as tests_medias
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.prompt.prompt_cleaning import cleanse_llm_keywords

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

    async def generate_mp3_from_text_async(self, prompt_text, target_file: str = None):
        logger.debug(f"Creating aa prompt from text: {prompt_text}")

        shutil.copy(
            src=tests_medias.get_test_prompt_recording_trainboy(), dst=target_file
        )

    async def generate_background_music_async(
        self, duration: float = 3, prompt: str = None, sleep_time: int = 0
    ) -> str:
        await asyncio.sleep(sleep_time)

        if duration is None:
            raise ValueError("Duration must be a float, got None")
        if duration < 0:
            raise ValueError(f"Duration must be a positive float, got {duration}")

        return tests_medias.get_sample_gen_background_music()

    async def generate_seine_transition_async(
        self, source_image_path, target_image_path, sleep_time: int = 0
    ):
        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        return tests_medias.get_test_seine_transition_video_path()  # Important:

    # the returned name should contains "transition" in the file name so we send the same video at the interpolate call
    # later on

    def cleanse_llm_keywords(self, input):
        return cleanse_llm_keywords(input)

    async def compose_music_from_text_async(
        self, prompt_text: str, duration: int, sleep_time: int = 0
    ):
        await asyncio.sleep(sleep_time)
        return tests_medias.get_sample_generated_music_path()

    async def get_music_generation_keywords_async(
        self, text, sleep_time: int = 0
    ) -> str:
        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        return "KEYWORDS FROM MUSIC GENERATION"

    async def interpolate_async(self, link_to_video: str, sleep_time: int = 0):
        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        local_file_path = Path(tests_medias.get_interpolate_video())
        local_file_url = urljoin("file:", pathname2url(str(local_file_path)))
        return local_file_url

    async def get_keywords_from_prompt(
        self, subtitleText, excluded_words: str = None, sleep_time: int = 0
    ):
        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        return "KEYWORDS FROM PROMPT", "keywords_from_prompt_file"

    async def get_keywords_from_prompt_async(
        self, subtitleText, excluded_words: str = None, sleep_time: int = 0
    ):

        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        return "KEYWORDS FROM PROMPT", "test title"

    async def get_enhanced_prompt_async(
        self, subtitleText, excluded_words: str = None, sleep_time: int = 0
    ):
        await asyncio.sleep(sleep_time)  # Simulate a long process with time.sleep
        return "ENHANCED FROM PROMPT", "test title"

    async def get_subtitles_async(self, audiofile_path, sleep_time: int = 0):

        logger.trace(f"Getting subtitles for {audiofile_path}")
        return await self.get_subtitles(
            audiofile_path=audiofile_path, sleep_time=sleep_time
        )

    async def get_subtitles(self, audiofile_path, sleep_time: int = 0):
        await asyncio.sleep(sleep_time)
        subs = None
        with open(os.path.join(_sample_media_dir, "subtitles.srt"), "r") as f:
            subs = f.read()
        return {"transcription": subs}

    async def generate_video_async(self, prompt, model_provider: str, aspect_ratio=(16,9), sleep_time: int = 0):
        await asyncio.sleep(sleep_time)

        if model_provider == "vikit":
            test_file = tests_medias.get_cat_video_path()
        elif model_provider == "stabilityai":
            test_file = tests_medias.get_stabilityai_image_video_path()
        elif model_provider == "" or model_provider is None:
            test_file = tests_medias.get_cat_video_path()
        elif model_provider == "haiper":
            test_file = tests_medias.get_haiper_video_path()
        elif model_provider == "videocrafter":
            test_file = tests_medias.get_videocrafter_video_path()
        elif model_provider == "stabilityai_image":
            test_file = tests_medias.get_stabilityai_image_video_path()
        elif model_provider == "dynamicrafter":
            test_file = tests_medias.get_dynamicrafter_image_video_path(prompt)
        elif model_provider == "runway":
            test_file = tests_medias.get_runway_image_video_path(prompt, aspect_ratio)
        else:
            raise ValueError(f"Unknown model provider: {model_provider}")

        if isinstance(prompt.text, str):
            logger.debug(
                f"Generating video from prompt: {prompt.text[:5]}, return a link: {test_file}"
            )
        # image-based prompt
        else:
            logger.debug(
                f"Generating video from prompt: {prompt.image[:5]}, return a link: {test_file}"
            )

        return test_file

    async def extract_audio_slice_async(
        self, i, end, audiofile_path, target_file_name: str = None, sleep_time: int = 0
    ):
        await asyncio.sleep(sleep_time)

    def extract_audio_slice(self, i, end, audiofile_path, target_file_name: str = None):
        return tests_medias.get_test_prompt_recording_trainboy()

    async def ask_gemini(self, prompt, more_contents= None):
        return "-1"
