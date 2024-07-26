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

from urllib.request import urlretrieve
from loguru import logger

from vikit.video.video import Video
from vikit.common.decorators import log_function_params
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType


class RawImageBasedVideo(Video):
    """
    Generates a video from raw image prompt
    """

    def __init__(
        self,
        title,
        raw_image_prompt: str = None,
    ):
        """
        Initialize the video

        Args:
            raw_image_prompt (base64: The raw image prompt to generate the video from
            title (str): The title of the video

        Raises:
            ValueError: If the source media URL is not set
        """
        if raw_image_prompt is None:
            raise ValueError("raw_image_prompt cannot be None")

        super().__init__()

        self._image = raw_image_prompt
        self._title = title
        self._needs_reencoding = False

    # def __str__(self) -> str:
    #     return super().__str__() + os.linesep + f"text: {self._text}"

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.RAWTEXT)

    @log_function_params
    def get_title(self):
        return self._title
        # else:
        #     # Add a unique identifier suffix to prevent several videos having the same title in a composite down the road
        #     self._title = summarised_title
        #     return self._title

    @log_function_params
    async def build(
        self,
        build_settings=VideoBuildSettings(),
    ):
        """
        Generate the actual inner video

        Params:
            - build_settings: allow some customization

        Returns:
            The current instance
        """

        super().build(build_settings)

        if self.metadata.is_video_built:
            return self

        logger.info("Generating video, could take some time ")
        ml_gateway = build_settings.get_ml_models_gateway()
        video_link_from_prompt = await ml_gateway.generate_video_async(
            self._image, model_provider=build_settings.target_model_provider
        )  # Should give a link on the Internet
        self.metadata.is_video_built = True

        if build_settings.interpolate:
            interpolated_video = await ml_gateway.interpolate_async(
                video_link_from_prompt
            )
            self.metadata.is_interpolated = True
            file_name = self.get_file_name_by_state(build_settings)
            interpolated_video_path = urlretrieve(
                interpolated_video,
                file_name,
            )[
                0
            ]  # Then we download it
            self.media_url = interpolated_video_path
            self.metadata.is_interpolated = True
        else:
            file_name = self.get_file_name_by_state(build_settings)
            self.media_url = video_link_from_prompt
            self.metadata.is_interpolated = False
        self._source = type(
            ml_gateway
        ).__name__  # The source of the video is used later to decide if we need to reencode the video

        return self
