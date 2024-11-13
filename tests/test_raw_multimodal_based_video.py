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

# from unittest.mock import patch, MagicMock, Mock
from vikit.video.raw_multimodal_based_video import RawMultiModalBasedVideo
from vikit.video.video import VideoBuildSettings

TEST_PROMPT_IMAGE = get_test_prompt_image()
TEST_PROMPT_AUDIO = get_test_prompt_recording()
TEST_PROMPT_VIDEO = get_cat_video_path()


class TestRawMultiModalBasedVideo:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_raw_image_based_video.txt", rotation="10 MB")

    @pytest.mark.local_integration
    async def test_get_title(self):
        with WorkingFolderContext():
            video_title = RawMultiModalBasedVideo(
                prompt=await PromptFactory(
                    ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
                ).create_prompt_from_multimodal_async(
                    image=TEST_PROMPT_IMAGE, text="test multimodal prompt", audio=TEST_PROMPT_AUDIO, video=TEST_PROMPT_VIDEO
                ),
                title="test_multimodal_prompt",
            ).get_title()
            logger.debug(f"Test get_title, video title: {video_title}")
            assert len(video_title) > 0  # we should have a file of at least 1 character

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_no_bg_music_without_subs(self):
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
            
            await pbvid.build(ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True))
            logger.debug(
                f"Test build_single_video_no_bg_music_without_subs, media URL: {pbvid.media_url}"
            )

            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert pbvid._background_music_file_name is None
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_no_bg_music_no_subtitles(self):
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

            await pbvid.build(ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True))

            assert pbvid._background_music_file_name is None
            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_with_default_bg_music_no_subtitles(self):
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
                ), ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
            )

            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_single_video_with_generated_bg_music_no_subtitles(self):
        with WorkingFolderContext():

            build_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                target_model_provider="runway",
            )
            multimodal_prompt = await PromptFactory().create_prompt_from_multimodal_async(
                image=TEST_PROMPT_IMAGE, text="test multimodal prompt", audio=TEST_PROMPT_AUDIO, video=TEST_PROMPT_VIDEO
            )

            video = RawMultiModalBasedVideo(
                prompt=multimodal_prompt,
                title="test_multimodal_prompt",
            )

            await video.build(build_settings=build_settings)

            assert video.media_url, "media URL was not updated"
            assert os.path.exists(video.media_url), "The generated video does not exist"
