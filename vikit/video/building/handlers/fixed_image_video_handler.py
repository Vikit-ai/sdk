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
import uuid as uid

from vikit.common.file_tools import download_or_copy_file
from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import generate_video_from_image
from vikit.common.file_tools import get_canonical_name

class FixedImageVideoGenHandler(Handler):

    async def execute_async(self, video: Video, ml_models_gateway: MLModelsGateway):

        logger.info(
            f"About to generate fixed image video: id: {video.id}, image: {video.prompt.image[:50]}"
        )

        tempUuid = str(uid.uuid4())

        image_path = await download_or_copy_file(
            url=video.prompt.image,
            local_path="for_fixed_image_video_" + get_canonical_name(video.prompt.image) + "." + video.prompt.image.split('.')[-1],
        )
        
        if video.prompt.duration is None:
            fixed_image_video = await generate_video_from_image(image_url = image_path)
        else:
            fixed_image_video = await generate_video_from_image(image_url = image_path, duration = video.prompt.duration)
        
        assert fixed_image_video, "Fixed image video video was not generated properly"

        video.media_url = fixed_image_video
        assert video.media_url, "Fixed image video was not downloaded properly"

        return video
