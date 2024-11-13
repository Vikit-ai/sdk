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

from loguru import logger
import time

from vikit.common.handler import Handler
from vikit.video.video import Video
from vikit.common.config import get_media_polling_interval
from vikit.common.file_tools import (
    url_exists,
)
from vikit.prompt.prompt import Prompt
from vikit.prompt.image_prompt import ImagePrompt
from vikit.prompt.prompt_factory import PromptFactory
from vikit.prompt.multimodal_prompt import MultiModalPrompt
from vikit.video.video import VideoBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.gateways.ML_models_gateway import MLModelsGateway
import copy


class VideoGenHandler(Handler):
    def __init__(self, video_gen_build_settings: VideoBuildSettings = None):
        if not video_gen_build_settings:
            raise ValueError("VideoBuildSettings is not set")
        self.video_gen_build_settings = video_gen_build_settings

    async def execute_async(self, video, ml_models_gateway: MLModelsGateway):
        """
        Process the video generation binaries: the video binary is generated from Gen AI, hosted behind an API
        which could be distant as well as local. The video binary is then stored in a web storage or locally.

        Important: The video generation is a long process, so it is executed asynchronously. Depending on the platform
        providing it, the video generation could take a few seconds to a few minutes, and the video binary might not be
        available immediately even though a URL is returned. This is not an issue on this handler but it might
        be for subsequent handlers as they will need to reprocess the video.

        Args:
            video (Video): The video to process

        Returns:
            The video with the media URL set to the generated video
        """
        logger.info(f"About to generate video: {video.id}, title: {video.get_title()}, prompt: {video.prompt}")
        logger.debug(
            f"Target Model provider in the handler: {self.video_gen_build_settings.target_model_provider}"
        )

        
        if video.prompt.build_settings.model_provider is None:
            model_provider=self.video_gen_build_settings.target_model_provider
        else:
            model_provider=video.prompt.build_settings.model_provider
        
        prompt_to_use = video.prompt
        if video.prompt.reengineer_text_prompt_from_image_and_text:
            new_prompt = copy.deepcopy(prompt_to_use)

            prompt = await PromptFactory().create_prompt_from_multimodal_async(text=new_prompt.text,  image=new_prompt.image)
            # Query Gemini to get an appropriate prompt
            new_prompt.text = (await ml_models_gateway.ask_gemini(prompt)).replace('"', '').replace("'", "")
            prompt_to_use = new_prompt

        video.media_url = (
            await (  # Should give a link on a web storage
                ml_models_gateway.generate_video_async(
                    prompt=prompt_to_use,
                    model_provider=model_provider,
                    aspect_ratio=self.video_gen_build_settings.aspect_ratio,
                )
            )
        )

        if not url_exists(video.media_url):
            logger.warning(
                f"Media URL {video.media_url} is not available yet, waiting for it for {get_media_polling_interval()} seconds"
            )
            time.sleep(get_media_polling_interval())
            if url_exists(video.media_url):
                return video.media_url
            else:
                logger.error(
                    f"Media URL {video.media_url} is not available yet, the related video will need to be generated after the overall video generation process"
                )

        logger.debug(f"Video generated from prompt: {video.media_url}")
        return video
