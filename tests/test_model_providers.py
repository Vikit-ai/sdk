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

import warnings
import pytest
from loguru import logger

from vikit.video.video import VideoBuildSettings
from vikit.video.composite_video import CompositeVideo
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.music_building_context import MusicBuildingContext
from tests.testing_tools import test_prompt_library
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.prompt.prompt_factory import PromptFactory
import tests.testing_tools as tools  # used to get a library of test prompts

prompt_mystic = tools.test_prompt_library["moss_stones-train_boy"]
logger.add("log_test_model_providers.txt", rotation="10 MB")
warnings.simplefilter("ignore", category=ResourceWarning)
warnings.simplefilter("ignore", category=UserWarning)


class TestModelProviders:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mix_providers_and_generate(self):
        with WorkingFolderContext():
            final_composite_video = CompositeVideo()
            # train_boy has 4 subtitles
            for i, subtitle in enumerate(test_prompt_library["train_boy"].subtitles):
                if i % 3 == 0:
                    target_model_provider = "vikit"
                elif i % 3 == 1:
                    target_model_provider = ""
                elif i % 3 == 2:
                    target_model_provider = "videocrafter"
                else:
                    target_model_provider = (None,)

                video = RawTextBasedVideo(subtitle.text)
                await video.prepare_build_hook(
                    build_settings=VideoBuildSettings(
                        test_mode=False,
                        music_building_context=MusicBuildingContext(),
                        target_model_provider=target_model_provider,
                    )
                )
                final_composite_video.append_video(video)

            await final_composite_video.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=False,
                    include_read_aloud_prompt=True,
                    prompt=test_prompt_library["train_boy"],
                )
            )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_model_provider_passing_and_error(self):
        with pytest.raises(ValueError):
            with WorkingFolderContext():
                video_build_settings = VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=True,
                    target_model_provider="an unexisting model",
                )

                prompt = (
                    "Unlock your radiance with AI Cosmetics."  # @param {type:"string"}
                )
                gw = video_build_settings.get_ml_models_gateway()
                prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(
                    prompt
                )
                video = PromptBasedVideo(prompt=prompt)
                logger.debug(
                    f"target_model_provider: {video_build_settings.target_model_provider}"
                )
                await video.build(build_settings=video_build_settings)
