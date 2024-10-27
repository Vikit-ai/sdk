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

# This test suite is used to test the audio compositions that can be made on videos,
# like using background music, adding subtitles, etc.
# It does not map exactly to one single file to test


import warnings

import pytest
from loguru import logger

from tests.testing_medias import (get_cat_video_path,
                                  get_generated_3s_forest_video_1_path,
                                  get_generated_3s_forest_video_2_path)
from tests.testing_tools import test_prompt_library
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
from vikit.video.building.handlers.gen_read_aloud_prompt_and_audio_merging_handler import \
    ReadAloudPromptAudioMergingHandler
from vikit.video.composite_video import CompositeVideo
from vikit.video.imported_video import ImportedVideo
from vikit.video.video import VideoBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


class TestAudioCompositions:

    def setUp(self) -> None:
        self.sample_video_path = get_cat_video_path()
        self.prompt_loosing_faith = None
        logger.add("log_test_audio_compositions.txt", rotation="10 MB")
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_insert_subtitle_audio_no_prompt(self):
        with pytest.raises(ValueError):
            handler = ReadAloudPromptAudioMergingHandler(None)
            await handler.execute_async(video=None)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_insert_subtitle_audio_nominal(self):
        with WorkingFolderContext():
            video = ImportedVideo(get_generated_3s_forest_video_1_path())
            handler = ReadAloudPromptAudioMergingHandler(
                recorded_prompt=test_prompt_library["moss_stones-train_boy"]
            )
            res_vid = await handler.execute_async(video=video, ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True))

            assert res_vid is not None, "Video was not generated properly"
            assert res_vid.media_url is not None, "Media URL was not generated properly"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_vcomp_w_bkg_music_and_prompt_based_subtitles(self):
        with WorkingFolderContext():
            video_start = ImportedVideo(get_generated_3s_forest_video_1_path())
            video_end = ImportedVideo(get_generated_3s_forest_video_2_path())
            test_video_mixer = CompositeVideo()
            final_video = test_video_mixer.append_video(video_start).append_video(
                video_end
            )
            final_video = await final_video.build(
                VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True
                    ),
                    include_read_aloud_prompt=True,
                    prompt=test_prompt_library["moss_stones-train_boy"],
                )
            )
            assert final_video.media_url is not None
            assert final_video.background_music is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_apply_generated_bg_sound_on_existing_gen_videos_composite(self):
        """
        Create a single video mix with 3 imported video and default bg music
        """
        with WorkingFolderContext():
            vid1 = ImportedVideo(get_generated_3s_forest_video_1_path())
            vid2 = ImportedVideo(get_generated_3s_forest_video_2_path())

            video_comp = CompositeVideo()
            video_comp.append_video(vid1).append_video(vid2)
            await video_comp.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                )
            )

            assert video_comp.background_music is not None, f"No background music set"
            assert video_comp.media_url is not None, f"No media URL"
            assert (
                video_comp.media_url != vid1.media_url
            ), f"Media URL is the same as the first video, {video_comp.media_url}"
            assert (
                video_comp.media_url != vid2.media_url
            ), f"Media URL is the same as the second video, {video_comp.media_url}"
