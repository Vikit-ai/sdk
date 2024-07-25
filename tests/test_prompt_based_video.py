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
import unittest
import pytest

from loguru import logger

import warnings

# from unittest.mock import patch, MagicMock, Mock
import tests.tests_medias as test_media
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.prompt.text_prompt import TextPrompt
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
import tests.tests_tools as tools  # used to get a library of test prompts
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestPromptBasedVideo(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt_based_video.txt", rotation="10 MB")

    @pytest.mark.unit
    def test_no_prompt_text(self):
        with pytest.raises(ValueError):
            _ = PromptBasedVideo(TextPrompt(""))

    @pytest.mark.local_integration
    def test_get_title(self):
        with WorkingFolderContext():
            video_title = PromptBasedVideo(
                PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                ).create_prompt_from_text("A group of stones")
            ).get_title()
            logger.debug(f"Test get_title, video title: {video_title}")
            assert len(video_title) > 0  # we should have a file of at least 1 character

    @pytest.mark.local_integration
    def test_build_single_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():

            pbvid = PromptBasedVideo(
                PromptFactory().create_prompt_from_text(
                    TEST_PROMPT, generate_recording=True
                )
            )
            pbvid.build()

            assert pbvid.media_url, "media URL was not updated"
            assert pbvid._background_music_file_name is None
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    def test_build_single_video_no_bg_music_with_subtitles(self):
        with WorkingFolderContext():
            pbvid = PromptBasedVideo(tools.test_prompt_library["moss_stones-train_boy"])
            pbvid.build(
                build_settings=VideoBuildSettings(include_audio_read_subtitles=True)
            )

            assert pbvid._background_music_file_name is None
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    def test_build_single_video_with_default_bg_music_with_subtitles(self):
        with WorkingFolderContext():
            pbvid = PromptBasedVideo(tools.test_prompt_library["moss_stones-train_boy"])
            pbvid.build(
                build_settings=VideoBuildSettings(
                    include_audio_read_subtitles=True,
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    ),
                )
            )

            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.integration
    def test_build_single_video_with_generated_bg_music_with_subtitles(self):
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                include_audio_read_subtitles=True,
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                test_mode=False,
            )

            pbvid = PromptBasedVideo(
                PromptFactory(
                    ml_gateway=bld_settings.get_ml_models_gateway()
                ).create_prompt_from_text(TEST_PROMPT, generate_recording=True)
            )
            pbvid.build(
                build_settings=bld_settings,
            )
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    def test_generate_short_video_single_sub(self):
        with WorkingFolderContext():
            pbv = PromptBasedVideo(
                PromptFactory().create_prompt_from_text("A group of stones in a forest")
            )
            result = pbv.build()
            assert result is not None
            assert os.path.exists(result.media_url)

    # @pytest.mark.local_integration
    # @unittest.skip("To be activated on case by case basis")
    # def test_use_sound_of_silence_original_audio_infer_subs_from_audio(self):
    #     """
    #     Test generating video from music prompt with original audio
    #     """
    #     with WorkingFolderContext():

    #         build_settings = VideoBuildSettings(
    #             music_building_context=MusicBuildingContext(
    #                 apply_background_music=True, use_recorded_prompt_as_audio=True
    #             ),
    #             include_audio_read_subtitles=False,
    #             test_mode=True,
    #         )

    #         original_recording_prompt = tools.test_prompt_library["sound of silence"]
    #         infered_prompt = PromptFactory(
    #             ml_gateway=build_settings.get_ml_models_gateway()
    #         ).create_prompt_from_audio_file(  # Here we create a prompt from audio
    #             original_recording_prompt._recorded_audio_prompt_path
    #         )
    #         build_settings.prompt = infered_prompt
    #         vid_sof = PromptBasedVideo(infered_prompt)
    #         vid_final = vid_sof.build(build_settings=build_settings)

    #         assert vid_final.media_url is not None
    #         assert vid_final.background_music is not None

    @pytest.mark.integration
    @unittest.skip("To be activated on case by case basis")
    def test_sound_of_silence(self):

        with WorkingFolderContext():
            bld_settings = VideoBuildSettings(
                include_audio_read_subtitles=True,
                musicBuildingContext=MusicBuildingContext(
                    generate_background_music=False,
                    apply_background_music=True,
                    use_recorded_prompt_as_audio=True,
                ),
                test_mode=False,
            )

            test_prompt = PromptFactory(
                bld_settings.get_ml_models_gateway()
            ).create_prompt_from_text(
                test_media.SOUND_OF_SILENCE, generate_recording=True
            )
            bld_settings.prompt = test_prompt

            video = PromptBasedVideo(test_prompt)
            vid_final = video.build(build_settings=bld_settings)

            assert vid_final.media_url is not None
            assert vid_final.background_music is not None

    @pytest.mark.integration
    def test_build_nominal_prompt_without_bk_music_wthout_subs(self):
        with WorkingFolderContext():
            build_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=False
                ),
                include_audio_read_subtitles=False,
                test_mode=False,
            )
            test_prompt = tools.test_prompt_library["moss_stones-train_boy"]
            video = PromptBasedVideo(test_prompt)
            video.build(build_settings=build_settings)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)

    @pytest.mark.integration
    # @unittest.skip("To be activated on case by case basis")
    def test_reunion_island_prompt_with_bk_music_subs(self):
        with WorkingFolderContext():
            bld_sett = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True
                ),
                include_audio_read_subtitles=True,
                test_mode=False,
            )
            test_prompt = PromptFactory(
                bld_sett.get_ml_models_gateway()
            ).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            video = PromptBasedVideo(prompt=test_prompt)
            video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)

    @pytest.mark.integration
    @unittest.skip("To be activated on case by case basis")
    def test_reunion_island_prompt_with_generated_bk_music_subs(self):
        with WorkingFolderContext():
            bld_sett = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                include_audio_read_subtitles=True,
                test_mode=False,
            )
            test_prompt = PromptFactory(
                bld_sett.get_ml_models_gateway()
            ).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            video = PromptBasedVideo(prompt=test_prompt)
            video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)

    @pytest.mark.local_integration
    @unittest.skip("To be activated on case by case basis")
    def test_local_int_reunion_island_prompt_with_bk_music_subs(self):
        with WorkingFolderContext():
            bld_sett = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True
                ),
                include_audio_read_subtitles=True,
                test_mode=False,
            )
            test_prompt = PromptFactory(
                bld_sett.get_ml_models_gateway()
            ).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            video = PromptBasedVideo(prompt=test_prompt)
            video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)

    @pytest.mark.local_integration
    def test_collab_integration(self):
        with WorkingFolderContext():
            video_build_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True, generate_background_music=True
                ),
                test_mode=True,
                include_audio_read_subtitles=True,
            )

            gw = video_build_settings.get_ml_models_gateway()
            prompt = PromptFactory(ml_gateway=gw).create_prompt_from_text(
                "A young girl traveling in the train alongside Mediterranean coast"
            )  # @param {type:"string"}

            video = PromptBasedVideo(prompt=prompt)

            video.build(build_settings=video_build_settings)
