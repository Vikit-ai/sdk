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

import base64
import os

from loguru import logger

import vikit.common.config as config
from vikit.common.decorators import log_function_params
from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.prompt.building.handlers.prompt_by_keywords_handler import (
    PromptByKeywordsHandler,
)
from vikit.prompt.building.handlers.prompt_by_raw_usertext_handler import (
    PromptByRawUserTextHandler,
)
from vikit.prompt.image_prompt import ImagePrompt
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.wrappers.ffmpeg_wrapper import get_media_duration

import uuid

class PromptFactory:
    """
    Prompt factory helps getting the right sub class of Prompt depending on
    the input provided. We use the right builder class to make it clear of the operations
    required to build each type of prompt and optimize it

    This is also useful to simplify unit testing of prompts as we will inject custom made Prompt objects
    instead of letting builders run some complex stuff involving external services
    """

    def __init__(
        self,
        ml_gateway: MLModelsGateway = None,
        prompt_build_settings: PromptBuildSettings = None,
    ):
        """
        Constructor of the prompt factory

        Args:
            ml_gateway: The ML Gateway to use to generate the prompt from the audio file

        """
        
        self.prompt_factory_uuid = str(uuid.uuid4())
        print("new uuid " + self.prompt_factory_uuid)
        prompt_build_settings = (
            prompt_build_settings if prompt_build_settings else PromptBuildSettings()
        )
        if ml_gateway:
            self._ml_gateway = ml_gateway
        else:
            self._ml_gateway = prompt_build_settings.get_ml_models_gateway()

    async def create_prompt_from_text(
        self, prompt_text: str = None, negative_prompt: str = None
    ):
        """
        Create a recorded prompt object from a text by  creating
        a recorded audio file using a ML Model, then extracting the subtitles,
        i.e. all the sentences text and timings

        args:
            - prompt_text: the text of the prompt
            - negative_prompt: the text for negative prompting (for the moment only applicable for haiper)

        returns:
            a RecordedPrompt object
        """
        if not prompt_text:
            raise ValueError("The prompt text is not provided")
        if len(prompt_text) == 0:
            raise ValueError("The prompt text is empty")
        extractor = None
        logger.debug(f"Creating prompt from text: {prompt_text}")
        # calling a model like Whisper from openAI
        await self._ml_gateway.generate_mp3_from_text_async(
            prompt_text=prompt_text,
            target_file=config.get_prompt_mp3_file_name(self.prompt_factory_uuid),
        )

        extractor = RecordedPromptSubtitlesExtractor()
        subs = await extractor.extract_subtitles_async(
            recorded_prompt_file_path=config.get_prompt_mp3_file_name(self.prompt_factory_uuid),
            ml_models_gateway=self._ml_gateway,
        )
        merged_subs = (
            extractor.merge_short_subtitles(  # merge short subtitles into larger ones
                subs, min_duration=config.get_subtitles_min_duration()
            )
        )

        prompt = RecordedPrompt(
            text=prompt_text,
            subtitles=merged_subs,
            audio_recording=config.get_prompt_mp3_file_name(self.prompt_factory_uuid),
            duration=get_media_duration(config.get_prompt_mp3_file_name(self.prompt_factory_uuid)),
        )
        prompt.negative_prompt = negative_prompt
        return prompt

    async def create_prompt_from_audio_file(
        self,
        recorded_audio_prompt_path: str = None,
    ):
        """
        Create a prompt object from a recorded audio file

        args:
            - recorded_audio_prompt_path: the path to the recorded audio file

        returns:
            self

        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If there's already a running loop, create a new task and wait for it
            return await loop.create_task(
                self.create_prompt_from_audio_file_async(
                    recorded_audio_prompt_path=recorded_audio_prompt_path
                )
            )
        else:
            # If no loop is running, use asyncio.run
            return asyncio.run(
                self.create_prompt_from_audio_file_async(
                    recorded_audio_prompt_path=recorded_audio_prompt_path
                )
            )

    async def create_prompt_from_audio_file_async(
        self,
        recorded_audio_prompt_path: str = None,
    ):
        """
        Create a prompt object from a recorded audio file

        args:
            - recorded_audio_prompt_path: the path to the recorded audio file

        returns:
            self

        """
        extractor = RecordedPromptSubtitlesExtractor()
        subs = await extractor.extract_subtitles_async(
            recorded_audio_prompt_path, ml_models_gateway=self._ml_gateway
        )
        merged_subs = extractor.merge_short_subtitles(
            subs, min_duration=config.get_subtitles_min_duration()
        )
        text = extractor.build_subtitles_as_text_tokens(merged_subs)
        prompt = RecordedPrompt(subtitles=merged_subs, text=text)
        await prompt.convert_recorded_audio_prompt_path_to_mp3(
            recorded_audio_prompt_path
        )

        return prompt

    async def get_reengineered_prompt_text_from_raw_text(
        self,
        prompt: str,
        prompt_build_settings: PromptBuildSettings,
    ) -> str:
        """
        Get a reengineered prompt from a raw text , using build settings
        to guide how we should build the prompt

        Args:
            prompt (str): The text prompt

        Returns:
            Prompt: The prompt object
        """
        handler_chain = self.get_prompt_handler_chain(prompt_build_settings)
        if len(handler_chain) == 0:
            return prompt
        else:
            for handler in handler_chain:
                text_prompt, video_suggested_title = await handler.execute_async(
                    text_prompt=prompt, prompt_build_settings=prompt_build_settings
                )

        return text_prompt  # return the last enhanced prompt from handlers chain

    def get_prompt_handler_chain(
        self, prompt_build_settings: PromptBuildSettings
    ) -> list[Handler]:
        """
        Get the handler chain of the Prompt. Can includes handlers to prepare
        the prompt text by adding more verbosity, or to filter offensive words, limit
        the prompt length, etc

        Args:
            build_settings (PromptBuildSettings): The settings to use for building the prompt

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        if prompt_build_settings.generate_from_llm_keyword:
            handlers.append(PromptByKeywordsHandler())
        if prompt_build_settings.generate_from_llm_prompt:
            handlers.append(PromptByRawUserTextHandler())

        return handlers

    @log_function_params
    def create_prompt_from_image(
        self,
        image_path: str = None,
        text: str = None,
    ):
        """
        Create a prompt object from a prompt image path

        args:
            - prompt_image: the image of the prompt

        returns:
            self
        """
        if image_path is None:
            raise ValueError("The prompt image is not provided")
        if not os.path.exists(image_path):
            raise ValueError(f"The prompt image file {image_path} does not exist")

        with open(image_path, "rb") as image_file:
            input_prompt_image = base64.b64encode(image_file.read()).decode("utf-8")
        img_prompt = ImagePrompt(prompt_image=input_prompt_image, text=text)
        return img_prompt
