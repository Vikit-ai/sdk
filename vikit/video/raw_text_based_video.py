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

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video import Video
from vikit.video.video_types import VideoType
from vikit.video.building.handlers.videogen_handler import (
    VideoGenHandler,
)
from vikit.common.handler import Handler


class RawTextBasedVideo(Video):
    """
    Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.
    This is currently the smallest building block available in the SDK, aimed to be used when you want more control
    over the video generation process.
    """

    def __init__(
        self,
        raw_text_prompt: str = None,
        title=None,
    ):
        """
        Initialize the video

        Args:
            raw_text_prompt (str): The raw text prompt to generate the video from
            title (str): The title of the video

        Raises:
            ValueError: If the source media URL is not set
        """
        if not raw_text_prompt:
            raise ValueError("text_prompt cannot be None")
        if len(raw_text_prompt) < 1:
            raise ValueError("No text_prompt provided")

        super().__init__()

        self.text = raw_text_prompt
        self._title = None
        if title:
            self._title = title
        else:
            self._title = self.get_title()
        self.metadata.title = self._title
        self._needs_video_reencoding = (
            False  # We usually don't need reencoding for raw text based videos
        )

    def __str__(self) -> str:
        return super().__str__() + os.linesep + f"text: {self.text}"

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWTEXT)

    def get_title(self):
        if self._title:
            return self._title
        else:
            # If no title existing yet (should be generated straight from an LLM)
            # then get the first and last words of the prompt
            splitted_prompt = self.text.split(" ")
            clean_title_words = [word for word in splitted_prompt if word.isalnum()]
            if len(clean_title_words) == 1:
                summarised_title = clean_title_words[0]
            else:
                summarised_title = clean_title_words[0] + "-" + clean_title_words[-1]

            # Add a unique identifier suffix to prevent several videos having the same title in a composite down the road
            self._title = summarised_title
            return self._title

    def run_build_core_logic_hook(self, build_settings: VideoBuildSettings):
        return super().run_build_core_logic_hook(build_settings)
        logger.info(f"Building video from raw text prompt: {self.text}")

    def get_core_handlers(self, build_settings) -> list[Handler]:
        """
         Get the handler chain of the video. Order matters here.
         At this stage, we should already have the enhanced prompt and title for this video

        Args:
             build_settings (VideoBuildSettings): The settings for building the video

         Returns:
             list: The list of handlers to use for building the video
        """
        handlers = []
        handlers.append(VideoGenHandler(video_gen_text_prompt=self.text))
        # if build_settings.interpolate:
        #     handlers.append(VideoInterpolationHandler())
        # Keeping this as commented, as we don't need to interpolate raw text based videos
        # using the latest models (quality is alreay excellent). This will be done depending on the provider in a next version
        return handlers
