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
import random

from loguru import logger

from vikit.common.config import get_max_file_size_url_gemini
from vikit.common.file_tools import download_or_copy_file
from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.wrappers.ffmpeg_wrapper import (
    cut_video,
    reverse_video,
)


class QualityCheckHandler(Handler):
    """
    Checks the quality of a video and rebuilds it if necessary

    Args:
        video_gen_handler (Handler): The video generation handler to call if the quality check is not qualitative enough
        is_good_until (function): The quality check function
        max_attempts (int): The maximum number of times to attempt the video generation.
        prompt_updater_fn (function): A optional hook function that updates the video
            generation prompt for each attempt. If not specified, the same prompt is
            reused for every attempt.

    Returns:
        The same video if the quality check was positive, and a regeneration if not
    """

    def __init__(
        self,
        video_gen_handler,
        is_good_until,
        max_attempts,
        prompt_updater_fn=None,
    ):
        if not video_gen_handler:
            raise ValueError("VideoGenHandler is not set")
        self.video_gen_handler = video_gen_handler
        self.is_good_until = is_good_until
        self.max_attempts = max_attempts
        self.prompt_updater_fn = prompt_updater_fn

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

        if (
            os.path.getsize(video.media_url) > get_max_file_size_url_gemini()
            and video.media_url_http
        ):
            is_good_up_to_secs = await self.is_good_until(
                video.media_url_http, ml_models_gateway
            )
        else:
            is_good_up_to_secs = await self.is_good_until(
                video.media_url, ml_models_gateway
            )
        return is_good_up_to_secs

    async def execute_async(
        self, video, ml_models_gateway: MLModelsGateway, min_good_secs=3
    ):
        """
        Checks the quality of a video and rebuilds it if necessary

        Args:
            video (Video): The video to process

        Returns:
            The same video if the quality check was positive, and a regeneration if not
        """
        logger.info(
            f"About to check quality of video: {video.id}, \
                    title: {video.get_title()}, prompt: {video.prompt}"
        )

        # The is_good_up_to_secs variable will either be -1 if the generated video is qualitative,
        # or the second at which a problem starts to appear.
        # It will be computed through the user provided is_good_until function,
        # because the definition of quality may vary depending on the video generation use-case
        if self.max_attempts > 1:
            is_good_up_to_secs = await self.get_is_good_up_to_secs_for_video(
                video, ml_models_gateway
            )
        else:
            # No need to check the quality as we are not doing any regenerations.
            is_good_up_to_secs = -1

        logger.debug(
            "After checking, video is qualitative \
                     until "
            + str(is_good_up_to_secs)
            + " seconds"
        )

        # Treat the provided video as attempt number 1.
        num_attempt = 1

        # If the video has not at least min_good_secs seconds of good quality, we need
        # to regenerate it as it is too short to show it to the user
        while (
            is_good_up_to_secs != -1
            and is_good_up_to_secs < min_good_secs
            and num_attempt < self.max_attempts
        ):
            num_attempt += 1
            logger.info(
                f"Quality check was negative, rebuilding Video {video.id} (attempt "
                f"{num_attempt}/{self.max_attempts})"
            )
            if self.prompt_updater_fn:
                video.prompt = self.prompt_updater_fn(video.prompt, num_attempt)
            video = await self.video_gen_handler.execute_async(
                video, ml_models_gateway=ml_models_gateway
            )

            is_good_up_to_secs = await self.get_is_good_up_to_secs_for_video(
                video, ml_models_gateway
            )

            logger.debug(
                "After another checking, video is qualitative until \
                         "
                + str(is_good_up_to_secs)
                + " seconds."
            )

        # If we made more than min_good_secs unsuccessful generation trials, the AI engine is not capable of
        # generating qualitative content. We just output the last video generated.
        if is_good_up_to_secs != -1:
            if is_good_up_to_secs < min_good_secs and num_attempt >= self.max_attempts:
                # Special case: we did min_good_secs trials and did not manage to
                # get at least min_good_secs qualitative seconds. We just keep the last video.
                logger.debug(
                    f"We did not manage to generate a qualitative \
                             video {video.id} with AI. Keeping the last video"
                )
                video.media_url = await cut_video(video.media_url, 0, 3, 5)
            else:
                logger.debug(
                    f"Video {video.id} is only qualitative \
                             until {is_good_up_to_secs}, reducing it"
                )
                video.media_url = await cut_video(
                    video.media_url, 0, is_good_up_to_secs, 5
                )
        else:
            video.media_url = await cut_video(video.media_url, 0, 3, 5)
        # Or else : is_good_up_to_secs = -1, we just keep the original built_video.media_url

        # We invert one video over 4
        random_int = random.randint(0, 4)
        if random_int == 3:
            video.media_url = await reverse_video(video.media_url)

        return video
