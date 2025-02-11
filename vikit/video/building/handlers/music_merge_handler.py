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

from vikit.common.handler import Handler
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.wrappers.ffmpeg_wrapper import get_media_duration, merge_audio


class MusicMergeHandler(Handler):
    def __init__(
        self,
        music_to_merge: str = None,
    ):
        self.music_to_merge = music_to_merge

    async def execute_async(self, video, ml_models_gateway=None):
        """
        Generate a background music based on the prompt and merge it with the video

        Args:
            video (Video): The video to process

        Returns:
            CompositeVideo: The composite video
        """

        logger.info(f"about to generate music for video: {video.id} ")

        video.metadata.bg_music_applied = True
        video.background_music = self.music_to_merge

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=self.music_to_merge,
            target_file_name=video.get_file_name_by_state(),
        )
        assert (
            video.background_music is not None
        ), "Background music was not generated properly"

        return video
