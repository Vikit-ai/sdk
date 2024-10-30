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

from tests.testing_medias import get_test_prompt_image
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


# from unittest.mock import patch, MagicMock, Mock
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.video.video import VideoBuildSettings

TEST_PROMPT = get_test_prompt_image()


class TestRawImagePromptBasedVideo:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_raw_image_based_video.txt", rotation="10 MB")

    @pytest.mark.local_integration
    async def test_get_title(self):
        with WorkingFolderContext():
            video_title = RawImageBasedVideo(
                prompt=await PromptFactory(
                    prompt_build_settings=PromptBuildSettings()
                )
                .create_prompt_from_image(
                    image=TEST_PROMPT, text="test image prompt"
                ),
                title="test_image_prompt",
            ).get_title()
            logger.debug(f"Test get_title, video title: {video_title}")
            assert len(video_title) > 0  # we should have a file of at least 1 character

    @pytest.mark.local_integration
    @pytest.mark.core_local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():
            image_prompt = await PromptFactory(
                prompt_build_settings=PromptBuildSettings()
            ).create_prompt_from_image(image=TEST_PROMPT, text="test image prompt")
            pbvid = RawImageBasedVideo(
                prompt=image_prompt,
                title="test_image_prompt",
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
            image_prompt = await PromptFactory(
                prompt_build_settings=PromptBuildSettings()
            ).create_prompt_from_image(image=TEST_PROMPT, text="test image prompt")
            pbvid = RawImageBasedVideo(
                prompt=image_prompt,
                title="test_image_prompt",
            )
            await pbvid.build(ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True))

            assert pbvid._background_music_file_name is None
            assert pbvid.media_url, f"media URL was not updated: {pbvid.media_url}"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_single_video_with_default_bg_music_no_subtitles(self):
        with WorkingFolderContext():
            image_prompt = await PromptFactory(
                prompt_build_settings=PromptBuildSettings()
            ).create_prompt_from_image(image=TEST_PROMPT, text="test image prompt")
            pbvid = RawImageBasedVideo(
                prompt=image_prompt,
                title="test_image_prompt",
            )
            await pbvid.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    ),
                    prompt=image_prompt,
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
                target_model_provider="stabilityai_image",
            )
            image_prompt = await PromptFactory().create_prompt_from_image(image=TEST_PROMPT, text="test image prompt")
            build_settings.prompt = image_prompt

            video = RawImageBasedVideo(
                prompt=image_prompt,
                title="test_image_prompt",
            )

            await video.build(build_settings=build_settings)

            assert video.media_url, "media URL was not updated"
            assert os.path.exists(video.media_url), "The generated video does not exist"
