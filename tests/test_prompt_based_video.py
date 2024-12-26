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

import pytest
from loguru import logger

# from unittest.mock import patch, MagicMock, Mock
import tests.testing_medias as test_media
import tests.testing_tools as tools  # used to get a library of test prompts
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.video import VideoBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestPromptBasedVideo:
    """
    Tests for PromptBasedVideo
    """

    @pytest.mark.unit
    def test_no_prompt_text(self):
        with pytest.raises(ValueError):
            _ = PromptBasedVideo(str(""))

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_title(self):
        with WorkingFolderContext():
            build_settings = VideoBuildSettings()
            prompt = await PromptFactory(
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                )
            ).create_prompt_from_text(
                "A group of stones",
            )

            video_title = PromptBasedVideo(prompt=prompt).get_title()
            assert len(video_title) > 0  # we should have a file of at least 1 character

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_prompt_based_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():
            pbvid = PromptBasedVideo(
                await PromptFactory(
                    ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                        test_mode=True
                    )
                ).create_prompt_from_text(
                    prompt_text=TEST_PROMPT,
                )
            )
            await pbvid.build(
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                )
            )

            assert pbvid.media_url, "media URL is None, was not updated"
            assert pbvid._background_music_file_name is None
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_prompt_based_video_no_bg_music_read_aloud_prompt(self):
        with WorkingFolderContext():
            pbvid = PromptBasedVideo(tools.test_prompt_library["moss_stones-train_boy"])
            await pbvid.build(
                build_settings=VideoBuildSettings(include_read_aloud_prompt=True),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert pbvid._background_music_file_name is None
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_build_prompt_based_video_with_default_bg_music_read_aloud_prompt(
        self,
    ):
        with WorkingFolderContext():
            pbvid = PromptBasedVideo(tools.test_prompt_library["moss_stones-train_boy"])
            await pbvid.build(
                build_settings=VideoBuildSettings(
                    include_read_aloud_prompt=True,
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    ),
                ),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )

            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_build_tom_cruse_video(self):
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                include_read_aloud_prompt=True,
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
            )

            prompt = await PromptFactory().create_prompt_from_text(
                """Tom Cruise's face reflects focus, his eyes filled with purpose and drive. He drives a moto very fast on a 
                skyscraper rooftop, jumps from the moto to an 
                helicopter, this last 3 seconds, then Tom Cruse dives into a swimming pool from the helicopter while the helicopter without pilot crashes 
                  near the beach"""
            )
            pbvid = PromptBasedVideo(prompt=prompt)

            pbvid = await pbvid.build(build_settings=bld_settings)
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.integration
    @pytest.mark.core_local_integration
    @pytest.mark.asyncio
    @pytest.mark.skip("duplicate?")
    async def test_build_prompt_based_video_with_generated_bg_music_read_aloud_prompt(
        self,
    ):
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                include_read_aloud_prompt=True,
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
            )

            prompt = await PromptFactory().create_prompt_from_text(TEST_PROMPT)
            pbvid = PromptBasedVideo(prompt=prompt)

            pbvid = await pbvid.build(
                build_settings=bld_settings,
            )
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_generate_prompt_based_video_single_sentence_sub(self):
        with WorkingFolderContext():

            prompt = await PromptFactory(
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                )
            ).create_prompt_from_text(
                "A group of stones in a forest",
            )
            pbv = PromptBasedVideo(prompt=prompt)
            result = await pbv.build(
                build_settings=VideoBuildSettings(prompt=prompt),
                ml_models_gateway=MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=True
                ),
            )
            assert result is not None
            assert os.path.exists(result.media_url)

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_use_recorded_prompt_infer_lyrics_sof(self):
        """
        Experimental: see how giving a music track would work as a prompt
            Letting the model infer the lyrics of the song
            Letting the model imagine a scenario vor the video with movie director's instructions
            use the audio track as a prompt

            ...please use your own music track for obvious copyright reasons :)
        """
        with WorkingFolderContext():
            bld_settings = VideoBuildSettings(
                include_read_aloud_prompt=True,
                musicBuildingContext=MusicBuildingContext(
                    generate_background_music=False,
                    apply_background_music=True,
                    use_recorded_prompt_as_audio=True,
                ),
            )

            test_prompt = await PromptFactory().create_prompt_from_text(
                test_media.sof,
            )
            bld_settings.prompt = test_prompt

            video = PromptBasedVideo(test_prompt)
            vid_final = await video.build(build_settings=bld_settings)

            assert vid_final.media_url is not None
            assert vid_final.background_music is not None

    # @pytest.mark.skip("To be activated on case by case basis")
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skip("skipping tests until needed to assess regressions")
    async def test_reunion_island_prompt_with_default_bk_music_subs(self):
        with WorkingFolderContext():
            bld_sett = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True
                ),
                include_read_aloud_prompt=True,
            )
            test_prompt = await PromptFactory().create_prompt_from_text(
                """A travel over Reunion Island, taken from bird-view at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
            )

            video = PromptBasedVideo(prompt=test_prompt)
            await video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_reunion_island_prompt_with_generated_bk_music_subs(self):
        with WorkingFolderContext():
            bld_sett = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                include_read_aloud_prompt=True,
            )
            test_prompt = await PromptFactory().create_prompt_from_text(
                """A travel over Reunion Island, taken from bird-view at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
            )

            video = PromptBasedVideo(prompt=test_prompt)
            await video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)
