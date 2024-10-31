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

from vikit.common.file_tools import url_exists
from vikit.common.handler import Handler
from vikit.video.video import Video
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.video.video import Video


class VideoBuildingHandlerTransition(Handler):

    async def execute_async(self, video: Video, ml_models_gateway: MLModelsGateway):
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        logger.info(
            f"about to generate transition as video: {video.id}, source:  {video.source_video.media_url}, target: {video.target_video.media_url}"
        )

        assert (
            video.source_video.media_url
        ), f"source video must be generated, video: {video.source_video}"
        assert (
            video.target_video.media_url
        ), f"target video must be generated, {video.target_video.media_url}, id: {video.target_video.id}"
        assert url_exists(video.source_video.media_url), "source_video must exist"
        assert url_exists(video.target_video.media_url), "target_video must exist"

        logger.debug(
            f"Applying transition from {video.source_video.media_url} to {video.target_video.media_url}"
        )
        
        # We generate a transition
        link_to_transition_video = await ml_models_gateway.generate_seine_transition_async(
            source_image_path=await video.source_video.get_last_frame_as_image(),
            target_image_path=await video.target_video.get_first_frame_as_image(),
        )

        if link_to_transition_video is None:
            raise ValueError("No link to transition video generated")
        video.media_url = link_to_transition_video
        video.metadata.is_video_built = True
        video.metadata.title = video.get_title()

        # target_file_name = video.get_file_name_by_state(
        #     build_settings=video.build_settings
        # )
        # target_file_name = await download_file(
        #     url=link_to_transition_video,
        #     local_path=video.get_file_name_by_state(video.build_settings),
        # )

        return video
