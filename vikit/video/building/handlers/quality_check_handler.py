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



import os
from loguru import logger
from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway import MLModelsGateway

from vikit.wrappers.ffmpeg_wrapper import (
    cut_video,
    create_zoom_video,
    reverse_video,
)
from vikit.common.config import get_max_file_size_url_gemini
from vikit.common.file_tools import (
    download_or_copy_file,
)

class QualityCheckHandler(Handler):
    """
    Checks the quality of a video and rebuilds it if necessary

    Args:
        video_gen_handler (Handler): The video generation handler to call if the quality check is not qualitative enough
        is_good_until (function): The quality check function

    Returns:
        The same video if the quality check was positive, and a regeneration if not
    """
    def __init__(self, video_gen_handler, is_good_until):
        if not video_gen_handler:
            raise ValueError("VideoGenHandler is not set")
        self.video_gen_handler = video_gen_handler
        self.is_good_until = is_good_until

    
    async def get_is_good_up_to_secs_for_video(self, video, ml_models_gateway): 
        """
        Gets the second until the video is considered good, or -1 if the video is qualitative.
        Args:
            video (Video): The video to test
            ml_models_gateway (MLModelGateway): The ML Models Gateway

        Returns:
            The second until the video is considered good, or -1
        """
        # Gemini does not support providing a link to a video if the size is superior to
        # get_max_length_url_gemini() (6.5mb by default)
        video.media_url = await download_or_copy_file(
            url=video.media_url,
            local_path=video.get_file_name_by_state(video.build_settings),
            force_download=True,
        )

        if (os.path.getsize(video.media_url) < get_max_file_size_url_gemini()
                and video.media_url_http):
            is_good_up_to_secs = await self.is_good_until(video.media_url_http, ml_models_gateway)
        else:
            is_good_up_to_secs = await self.is_good_until(video.media_url, ml_models_gateway)
        return is_good_up_to_secs

    async def execute_async(self, video, ml_models_gateway: MLModelsGateway, max_attempts=4, min_good_secs = 3):
        """
        Checks the quality of a video and rebuilds it if necessary

        Args:
            video (Video): The video to process

        Returns:
            The same video if the quality check was positive, and a regeneration if not
        """
        logger.info(f"About to check quality of video: {video.id}, \
                    title: {video.get_title()}, prompt: {video.prompt}")
        
        # The is_good_up_to_secs variable will either be -1 if the generated video is qualitative,
        # or the second at which a problem starts to appear.
        # It will be computed through the user provided is_good_until function,
        # because the definition of quality may vary depending on the video generation use-case
        is_good_up_to_secs = None

        

        # Gemini does not support providing a link to a video if the size is superior to
        # get_max_length_url_gemini() (6.5mb by default)
        is_good_up_to_secs = await self.get_is_good_up_to_secs_for_video(video, ml_models_gateway)

        logger.debug("After checking, video is qualitative \
                     until " + str(is_good_up_to_secs) + " seconds")

        # If the video has not at least min_good_secs seconds of good quality, we need to regenerate it as it is
        # too short to show it to the user
        num_attempts = 0
        while is_good_up_to_secs != -1 and is_good_up_to_secs < min_good_secs and num_attempts < max_attempts :
            logger.info(f"Quality check was negative, rebuilding Video {video.id} ")
            video = await self.video_gen_handler.execute_async(video,
                                                               ml_models_gateway=ml_models_gateway)

            is_good_up_to_secs = await self.get_is_good_up_to_secs_for_video(video, ml_models_gateway)

            logger.debug("After another checking, video is qualitative until \
                         " + str(is_good_up_to_secs) + " seconds.")
            num_attempts = num_attempts + 1

        # If we made more than min_good_secs unsuccessful generation trials, the AI engine is not capable of
        # generating qualitative content. We just output a naive zoom video if we have an image,
        # and discard the video if we just have text
        # If the video has min_good_secs or more seconds of qualitative content,
        # we can cut it to discard unqualitative content
        # If the video is qualitative (function results -1),
        # we just keep the media_url we had before unchanged
        if is_good_up_to_secs != -1:
            if is_good_up_to_secs < min_good_secs and num_attempts >= max_attempts:
                # Special case: we did min_good_secs trials and did not manage to
                # get at least min_good_secs qualitative seconds
                logger.debug(f"We did not manage to generate a qualitative \
                             video {video.id} with AI")
                if (hasattr(video.prompt, 'image') and video.prompt.image is not None):
                    logger.debug(f"Generating video {video.id} with ffmpeg by zooming in")
                    video.media_url = await reverse_video(
                                                    await create_zoom_video(video.prompt.image))
                else:
                    logger.debug(f"Discarding video {video.id}")
                    video.discarded = True
            else:
                logger.debug(f"Video {video.id} is only qualitative \
                             until {is_good_up_to_secs}, reducing it")
                video.media_url = await cut_video(video.media_url, 0, is_good_up_to_secs, 5)
        #Or else : is_good_up_to_secs = -1, we just keep the original built_video.media_url

        return video
