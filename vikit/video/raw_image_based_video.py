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
from vikit.prompt.prompt_factory import PromptFactory


class RawImageBasedVideo(Video):
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
        self.duration = 4.0  # Currently generated videos are 4 seconds long; this will be variable per model later

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
                description=self.text
            )
        else:
            summarised_title = "ImagePrompt"
        self.metadata.title = summarised_title
        return self.metadata.title

    def get_duration(self):
        return self.duration

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

    async def is_qualitative(self, media_url, ml_models_gateway): 
        prompt = await PromptFactory().create_prompt_from_multimodal_async(text="At what second is the camera revealing more of the scene not present at the begining (except object details), or showing blurry things ? If it does, respond the second else -1. Just respond the second or -1 nothing else. Do not get wrong. Most of the time, camera zooming in is -1 and else the second.",  video=media_url)
        response = await ml_models_gateway.ask_gemini(prompt)
        return ("-1" in response)

    async def is_qualitative_until(self, media_url, ml_models_gateway): 
        prompt = await PromptFactory().create_prompt_from_multimodal_async(text="""
You are an part of a program that will determine if a video will be trimmed if yes you will output the second and if not -1.
    
Perform a frame-by-frame analysis of the provided video. For each frame, define the visible structural elements that are visible in the image (but do not oupput them). These elements could be seen also through the mirrors as well. You should name the elements only and only based on what you see in the image. Examples of structural elements could be furniture, doors, windows, walls, portions of walls, radiator, plants, objects or openings, if and only if they are visible in the given image.

Then, identify the second at which any new structural element or any new portion of a structural element or any change in visibility of a structural element or any differences in the spatial extent of the structural elements shown or any new part of the scene or any blurry thing first appears. If nothing of this happens, respond with -1.

Output ONLY the second or -1 nothing else. No other text or characters are allowed. Do not get wrong. Do not output any text.
        """,  video=media_url)
        response = await ml_models_gateway.ask_gemini(prompt)
        return int(response)
