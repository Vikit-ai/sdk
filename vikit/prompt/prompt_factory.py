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
from vikit.prompt.multimodal_prompt import MultiModalPrompt
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.wrappers.ffmpeg_wrapper import get_media_duration
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

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
        ml_models_gateway: MLModelsGateway = None,
        prompt_build_settings: PromptBuildSettings = PromptBuildSettings(),
    ):
        """
        Constructor of the prompt factory

        Args:
            ml_models_gateway: The ML Gateway to use to generate the prompt from the audio file

        """
        
        self.prompt_factory_uuid = str(uuid.uuid4())
        self.prompt_build_settings = prompt_build_settings

        logger.debug("New PromptFactory uuid " + self.prompt_factory_uuid)

        if ml_models_gateway:
            self.ml_models_gateway = ml_models_gateway
        else:
            self.ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=False)

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
        await self.ml_models_gateway.generate_mp3_from_text_async(
            prompt_text=prompt_text,
            target_file=config.get_prompt_mp3_file_name(self.prompt_factory_uuid),
        )

        extractor = RecordedPromptSubtitlesExtractor()
        subs = await extractor.extract_subtitles_async(
            recorded_prompt_file_path=config.get_prompt_mp3_file_name(self.prompt_factory_uuid),
            ml_models_gateway=self.ml_models_gateway,
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
            build_settings=self.prompt_build_settings,
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
            recorded_audio_prompt_path, ml_models_gateway=self.ml_models_gateway
        )
        merged_subs = extractor.merge_short_subtitles(
            subs, min_duration=config.get_subtitles_min_duration()
        )
        text = extractor.build_subtitles_as_text_tokens(merged_subs)
        prompt = RecordedPrompt(subtitles=merged_subs, text=text, build_settings=self.prompt_build_settings)
        await prompt.convert_recorded_audio_prompt_path_to_mp3(
            recorded_audio_prompt_path
        )

        return prompt

    async def get_reengineered_prompt_text_from_raw_text(
        self,
        prompt: str,
        prompt_build_settings: PromptBuildSettings = PromptBuildSettings(),
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
                    text_prompt=prompt, prompt_build_settings=prompt_build_settings, ml_models_gateway=self.ml_models_gateway
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
    async def create_prompt_from_image(
        self,
        image: str = None,
        text: str = None,
        reengineer_text:bool = False,
        model_provider: str= None,
        reengineer_text_prompt_from_image_and_text=False,
    ):
        """
        Create a prompt object from a prompt image path

        args:
            - image: the path of the image of the prompt

        returns:
            self
        """
        if image is None:
            raise ValueError("The prompt image is not provided")
        
        if reengineer_text:
            text = await get_reengineered_prompt_text_from_raw_text(text, self.prompt_build_settings)

        img_prompt = MultiModalPrompt(image=image, text=text, model_provider=model_provider, build_settings=self.prompt_build_settings, reengineer_text_prompt_from_image_and_text=reengineer_text_prompt_from_image_and_text)
        return img_prompt

    async def create_prompt_from_multimodal_async(
        self,
        text: str = None, 
        reengineer_text:bool = False,
        negative_text: str = None,
        image: str = None, 
        audio: str = None, 
        video:str = None, 
        duration:float = None,
        seed: int = None,
        model_provider: str= None,
        reengineer_text_prompt_from_image_and_text=False,
    ):
        """
        Create a prompt object from a prompt image path

        args:
            - text: the text of the prompt
            - image: the image base64, URL or URI of the prompt
            - audio: the audio base64, URL or URI of the prompt
            - video: the video base64, URL or URI of the prompt
            - duration: expected duration of output

        returns:
            self
        """
        if text is None and image is None and audio is None and video is None:
            raise ValueError("No prompt data is provided")
        
        if reengineer_text:
            text = await get_reengineered_prompt_text_from_raw_text(text, self.prompt_build_settings)

        multimodal_prompt = MultiModalPrompt(text=text, negative_text=negative_text, image=image, audio=audio, video=video, duration=duration, seed=seed, model_provider=model_provider, build_settings=self.prompt_build_settings, reengineer_text_prompt_from_image_and_text=reengineer_text_prompt_from_image_and_text)
        return multimodal_prompt
