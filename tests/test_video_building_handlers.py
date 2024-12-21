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

import pytest
from loguru import logger

from tests.testing_medias import get_test_prompt_recording_trainboy
from vikit.common.context_managers import WorkingFolderContext
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.video.building.handlers.use_prompt_audio_track_and_audio_merging_handler import (
    UsePromptAudioTrackAndAudioMergingHandler,
)
from vikit.video.building.handlers.videogen_handler import VideoGenHandler
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video_build_settings import VideoBuildSettings

from vikit.prompt.prompt_factory import PromptFactory
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


class TestVideoBuildingHandlers:
    """
    Test the video building handlers
    """

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_VideoBuildingHandlerGenerateFomApi(self):
        with WorkingFolderContext():
            vid = RawTextBasedVideo(raw_text_prompt="test")
            vid.build_settings = VideoBuildSettings()

            test_gateway = MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=True
            )

            prompt = await PromptFactory(test_gateway).create_prompt_from_text("test")
            api_handler = VideoGenHandler(video_gen_build_settings=vid.build_settings)
            video_built = await api_handler.execute_async(
                video=vid, ml_models_gateway=test_gateway
            )
            assert video_built is not None, "Video built should not be None"
            logger.debug(f"Video built media: {video_built.media_url}")
            assert (
                video_built.media_url is not None
            ), "Video built should have a media url"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_use_prompt_audio_track(self):
        with WorkingFolderContext():
            vid = RawTextBasedVideo(raw_text_prompt="test")
            prompt = RecordedPrompt()
            prompt.audio_recording = get_test_prompt_recording_trainboy()
            await vid.build(
                build_settings=VideoBuildSettings(prompt=prompt),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )
            assert vid is not None, "Video built should not be None"
            assert vid.media_url is not None, "Video built should have a media url"

            handler = UsePromptAudioTrackAndAudioMergingHandler()
            video__merged_with_prompt_original_audio = await handler.execute_async(
                video=vid
            )
            assert (
                video__merged_with_prompt_original_audio is not None
            ), "Video built should not be None"
