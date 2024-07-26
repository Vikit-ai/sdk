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

from vikit.video.video import Video
from vikit.common.handler import Handler


class VideoGenHandler(Handler):
    def __init__(self, video_gen_text_prompt: str = None):
        if not video_gen_text_prompt:
            raise ValueError("Prompt text is not set")
        self.video_gen_prompt_text = video_gen_text_prompt

    async def execute_async(self, video: Video):
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        logger.info(f"About to generate video: {video.id}, title: {video.get_title()}")
        video.media_url = (
            await (  # Should give a link on a web storage
                video.build_settings.get_ml_models_gateway().generate_video_async(
                    prompt=self.video_gen_prompt_text,
                    model_provider=video.build_settings.target_model_provider,
                )
            )
        )
        video.is_video_generated
        video.metadata.is_video_generated = True

        logger.debug(f"Video generated from prompt: {video.media_url[:50]}")
        return video
