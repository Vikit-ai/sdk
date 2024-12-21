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

from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video import VideoBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


class TestRawTextBasedVideo:
    """
    Tests for RawTextBasedVideo
    """

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_video_mix_with_empty_video(self):
        with pytest.raises(ValueError):
            _ = RawTextBasedVideo(raw_text_prompt=None)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_create_video_from_basic_text_prompt(
        self,
    ):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            built = await video.build(
                build_settings=VideoBuildSettings(),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert built.media_url is not None

    @pytest.mark.local_integration
    @pytest.mark.core_local_integration
    @pytest.mark.asyncio
    async def test_output_video_file_name(
        self,
    ):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            built = await video.build(
                build_settings=VideoBuildSettings(
                    output_video_file_name="my_video.mp4"
                ),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert built.media_url is not None
            assert os.path.exists(
                "my_video.mp4"
            ), f"File not found: my_video.mp4, {os.listdir()}"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_target_path(
        self,
    ):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            target_path = os.makedirs("testdir")
            built = await video.build(
                build_settings=VideoBuildSettings(target_dir_path="testdir"),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert built.media_url is not None
            assert os.path.isdir("testdir"), f"Directory not found: {target_path}"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_target_path_and_output_file_name(
        self,
    ):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a prompt text")
            target_path = os.makedirs("testdir2")
            built = await video.build(
                build_settings=VideoBuildSettings(
                    target_dir_path="testdir2",
                    output_video_file_name="my_othervideo.mp4",
                ),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert built.media_url is not None
            assert os.path.isdir("testdir2"), f"Directory not found: {target_path}"
