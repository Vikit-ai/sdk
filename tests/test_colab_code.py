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
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.video import VideoBuildSettings

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestColabCode:

    def setUp(self) -> None:
        logger.add("log_test_colab.txt", rotation="10 MB")
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_radiance_cosmetics(self):
        working_folder = "./examples/inputs/PromptbasedVideo/"
        with WorkingFolderContext(working_folder):
            video_build_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                include_read_aloud_prompt=True,
                target_model_provider="luma",  # Available models: videocrafter, stabilityai, haiper, runway & luma
                output_video_file_name="AICosmetics.mp4",
                interpolate=True,
            )

            prompt = "Unlock your radiance with AI Cosmetics. Experience the magic of premium ingredients, designed to reveal your natural glow. Discover the perfect blend of science and nature with our advanced formulations, tailored to enhance your unique beauty. Transform your skincare routine with our luxurious, high-performance products that deliver visible results. Embrace your true self with confidence, knowing AI Cosmetics has you covered every step of the way."  # @param {type:"string"}

            prompt = await PromptFactory().create_prompt_from_text(prompt)
            video = PromptBasedVideo(prompt=prompt)
            await video.build(build_settings=video_build_settings)

            assert video.media_url, "media URL is None, was not updated"
            assert video._background_music_file_name is not None
            assert os.path.exists(video.media_url), "The generated video does not exist"
