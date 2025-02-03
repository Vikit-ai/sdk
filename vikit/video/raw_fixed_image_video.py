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

from vikit.common.decorators import log_function_params
from vikit.common.handler import Handler
from vikit.video.building.handlers.videogen_handler import VideoGenHandler
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType
from vikit.video.building.handlers.fixed_image_video_handler import FixedImageVideoGenHandler
from vikit.prompt.prompt import Prompt
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.building.handlers.interpolation_handler import (
    VideoInterpolationHandler,
)
from vikit.video.building.handlers.quality_check_handler import (
    QualityCheckHandler,
)


class RawFixedImageVideo(Video):
    """
    Generates a video from raw image prompt
    """

    def __init__(
        self,
        title: str = None,
        prompt: Prompt = None,
    ):
        """
        Initialize the video

        Args:
            prompt (Prompt: The image prompt to generate the video from
            title (str): The title of the video

        Raises:
            ValueError: If the source media URL is not set
        """
        if prompt is None:
            raise ValueError("prompt cannot be None")

        super().__init__(prompt)

        self._needs_reencoding = False
        if title:
            self.metadata.title = title

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWIMAGE)

    @log_function_params
    def get_title(self):
        if self.metadata.title:
            summarised_title = self.get_title_from_description(
                description=self.metadata.title
            )
        elif self.prompt and self.prompt.text:
            summarised_title = self.get_title_from_description(
                description=self.prompt.text
            )
        else:
            summarised_title = "FixedImageVideo"
        self.metadata.title = summarised_title
        return self.metadata.title

    def get_duration(self):
        return self.duration

    def run_build_core_logic_hook(self, build_settings: VideoBuildSettings, 
                                  ml_models_gateway):
        return super().run_build_core_logic_hook(build_settings, ml_models_gateway)

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
        fixed_image_video_handler = FixedImageVideoGenHandler()
        handlers.append(
            fixed_image_video_handler
        )

        if build_settings.interpolate:
            handlers.append(VideoInterpolationHandler())
        return handlers