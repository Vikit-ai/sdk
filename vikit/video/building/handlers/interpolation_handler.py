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

from vikit.common.file_tools import download_or_copy_file
from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.video.video import Video


class VideoInterpolationHandler(Handler):

    async def execute_async(self, video: Video, ml_models_gateway: MLModelsGateway):

        logger.info(
            f"About to interpolate video: id: {video.id}, media: {video.media_url[:50]}"
        )

        interpolated_video = (
            await ml_models_gateway.interpolate_async(
                video.media_url
            )
        )
        assert interpolated_video, "Interpolated video was not generated properly"
        video.metadata.is_interpolated = True

        interpolated_video_path = await download_or_copy_file(
            url=interpolated_video,
            local_path=video.get_file_name_by_state(video.build_settings),
        )

        video.media_url = interpolated_video_path
        assert video.media_url, "Interpolated video was not downloaded properly"

        return video
