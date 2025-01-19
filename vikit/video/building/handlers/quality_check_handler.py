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
from vikit.common.config import get_max_file_size_url_gemini
import os
from vikit.wrappers.ffmpeg_wrapper import (
    get_first_frame_as_image_ffmpeg,
    get_last_frame_as_image_ffmpeg,
    get_media_duration,
    cut_video,
    create_zoom_video,
    reverse_video,
)
from vikit.common.file_tools import (
    download_or_copy_file,
)

class QualityCheckHandler(Handler):
    def __init__(self, video_gen_handler = None):
        if not video_gen_handler:
            raise ValueError("VideoGenHandler is not set")
        self.video_gen_handler = video_gen_handler

    async def execute_async(self, video, ml_models_gateway: MLModelsGateway, quality_check = None):
        """
        Checks the quality of a video and rebuilds it if necessary

        Args:
            video (Video): The video to process
            quality_check (function): The quality check function

        Returns:
            The same video if the quality check was positive, and a regeneration if not
        """
        logger.info(f"About to check quality of video: {video.id}, title: {video.get_title()}, prompt: {video.prompt}")

        is_qualitative_until = -1

        video.media_url = await download_or_copy_file(
            url=video.media_url,
            local_path=video.get_file_name_by_state(video.build_settings),
        )

        #Gemini does not support providing a link to a video if the size is superior to get_max_length_url_gemini() (6.5mb by default)
        if (os.path.getsize(video.media_url) < get_max_file_size_url_gemini() and video.media_url_http): 
            is_qualitative_until = await quality_check(video.media_url_http, ml_models_gateway)
        else:
            is_qualitative_until = await quality_check(video.media_url, ml_models_gateway)
        logger.debug("After checking, video is qualitative until " + str(is_qualitative_until) + " seconds")
        
        #If the video has not at least 3 seconds of good quality, we need to regenerate it as it is too short to show it to the user
        regeneration_number = 0
        while is_qualitative_until != -1 and is_qualitative_until < 3 and regeneration_number < 4 :

            # if regeneration_number == 1:
            #     addFirstTry = " with a slight upward tilt. The zoom should be gradual, and the upward motion should be subtle to keep the focus on the center of the frame."
            #     video.prompt.text = video.prompt.text + addFirstTry
            #     video.prompt.reengineer_text_prompt_from_image_and_text = False
            # elif regeneration_number == 2:
            #     video.prompt.text = "Make only a camera movement on the central element of this photo. Do not add any unreal elements or modifications to the property."
            #     video.prompt.reengineer_text_prompt_from_image_and_text = False
            # elif regeneration_number == 3: 
            #     video.prompt.text = "Make only a camera movement zoom in on the main element of this photo. The video should feel polished, modern, and visually appealing, resembling high-quality real estate marketing videos used by luxury agencies. Do not add any unreal elements or modifications to the property"
            #     video.prompt.reengineer_text_prompt_from_image_and_text = False
            logger.info(f"Quality check was negative, rebuilding Video {video.id} ")
            video = await self.video_gen_handler.execute_async(video, ml_models_gateway=ml_models_gateway)
            video.media_url = await download_or_copy_file(
                url=video.media_url,
                local_path=video.get_file_name_by_state(video.build_settings),
            )
            if (os.path.getsize(video.media_url) < get_max_file_size_url_gemini() and video.media_url_http): 
                is_qualitative_until = await quality_check(video.media_url_http, ml_models_gateway)
            else:
                is_qualitative_until = await quality_check(video.media_url, ml_models_gateway)
            logger.debug("After another checking, video is qualitative until " + str(is_qualitative_until) + " seconds.")
            regeneration_number = regeneration_number + 1
        
        #If we made more than 3 unsuccessful generation trials, the AI engine is not capable of generaing qualitative content. We just output a naive zoom video if we have an image, and discard the video if we just have text
        #If the video has 3 or more seconds of qualitative content, we can cut it to discard unqualitative content
        #If the video is qualitative (function results -1), we just keep the media_url we had before unchanged
        if is_qualitative_until != -1:
            if is_qualitative_until < 3 and regeneration_number >= 4: #Special case: we did 3 trials and did not manage to get at least 3 qualitative seconds
                logger.debug(f"We did not manage to generate a qualitative video {video.id} with AI")
                if (hasattr(video.prompt, 'image') and video.prompt.image is not None):
                    logger.debug(f"Generating video {video.id} with ffmpeg by zooming in")
                    video.media_url = await reverse_video(await create_zoom_video(video.prompt.image))
                else:
                    logger.debug(f"Discarding video {video.id}")
                    video.discarded = True
            else:
                logger.debug(f"Video {video.id} is only qualitative until {is_qualitative_until}, reducing it")
                # cutVideoUntil = 3
                # if is_qualitative_until > 3: 
                #     cutVideoUntil = is_qualitative_until
                video.media_url = await cut_video(video.media_url, 0, 3, 5)
        #Else : is_qualitative_until = -1, we just keep the original built_video.media_url

        return video
