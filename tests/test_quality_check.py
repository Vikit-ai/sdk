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
import warnings

import pytest
from loguru import logger

from tests.testing_medias import get_test_prompt_image, get_test_prompt_recording, get_cat_video_path
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

from vikit.video.raw_multimodal_based_video import RawMultiModalBasedVideo
from vikit.video.video import VideoBuildSettings

TEST_PROMPT_IMAGE = get_test_prompt_image()
TEST_PROMPT_AUDIO = get_test_prompt_recording()
TEST_PROMPT_VIDEO = get_cat_video_path()

async def dummy_quality_check(media_url, ml_models_gateway):
    return -1

async def dummy_quality_check_negative(media_url, ml_models_gateway):
    return 0

class TestRawMultiModalBasedVideo:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_raw_image_based_video.txt", rotation="10 MB")

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_quality_check_multimodal(self):
        with WorkingFolderContext():
            multimodal_prompt = await PromptFactory(
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
            ).create_prompt_from_multimodal_async(
                image=TEST_PROMPT_IMAGE, text="test multimodal prompt", audio=TEST_PROMPT_AUDIO, video=TEST_PROMPT_VIDEO
            )
            pbvid = RawMultiModalBasedVideo(
                prompt=multimodal_prompt,
                title="test_multimodal_prompt",
            )
            await pbvid.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    )
                ), ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True), quality_check=dummy_quality_check
            )

            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_quality_check_multimodal_negative(self):
        with WorkingFolderContext():
            multimodal_prompt = await PromptFactory(
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
            ).create_prompt_from_multimodal_async(
                image=TEST_PROMPT_IMAGE, text="test multimodal prompt", audio=TEST_PROMPT_AUDIO, video=TEST_PROMPT_VIDEO
            )
            pbvid = RawMultiModalBasedVideo(
                prompt=multimodal_prompt,
                title="test_multimodal_prompt",
            )
            await pbvid.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    )
                ), ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True), quality_check=dummy_quality_check_negative
            )

            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"