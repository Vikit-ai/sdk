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
from vikit.prompt.prompt import Prompt
from vikit.prompt.multimodal_prompt import MultiModalPrompt
from vikit.prompt.prompt_factory import PromptFactory

class RawMultiModalBasedVideo(Video):
    """
    Generates a video from raw multimodal prompt, i.e. very similar to calling a mainstream video generation platform.
    This is currently a small building block available in the SDK, aimed to be used when you want more control
    over the video generation process.
    """

    def __init__(
        self,
        title: str = None,
        prompt: MultiModalPrompt = None,
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
            raise ValueError("raw_image_prompt cannot be None")

        super().__init__(prompt)

        self._needs_reencoding = False
        if title:
            self.metadata.title = title
        if prompt.duration is None:
            self.duration = 5.0
        else:
            self.duration = prompt.duration

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWMULTIMODAL)

    def run_build_core_logic_hook(self, build_settings: VideoBuildSettings, ml_models_gateway, quality_check=None):
        return super().run_build_core_logic_hook(build_settings, ml_models_gateway, quality_check)

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
        handlers.append(
            VideoGenHandler(video_gen_build_settings=build_settings)
        )
        return handlers