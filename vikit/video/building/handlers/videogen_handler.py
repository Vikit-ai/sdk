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


class VideoGenHandler(Handler):
    def __init__(self, video_gen_text_prompt: str = None):
        if not video_gen_text_prompt:
            raise ValueError("Prompt text is not set")
        self.video_gen_prompt_text = video_gen_text_prompt

    async def execute_async(self, video: Video):
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
        logger.info(f"About to generate video: {video.id}, title: {video.get_title()}")
        logger.debug(
            f"Target Model provider in the handler: {video.build_settings.target_model_provider}"
        )
        video.media_url = (
            await (  # Should give a link on a web storage
                video.build_settings.get_ml_models_gateway().generate_video_async(
                    prompt=self.video_gen_prompt_text,
                    model_provider=video.build_settings.target_model_provider,
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
