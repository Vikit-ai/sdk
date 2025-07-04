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

import math
import os
import warnings

import pytest
from loguru import logger

import tests.testing_medias as tests_medias
from vikit.common.context_managers import WorkingFolderContext
from vikit.wrappers.ffmpeg_wrapper import (
    concatenate_videos,
    create_zoom_video,
    cut_video,
    extract_audio_from_video,
    generate_video_from_image,
    get_media_duration,
    reencode_video,
)


class TestFFMPEGWrapper:
    """
    Test the ffmpeg wrapper
    """

    def setup(self):
        logger.add("log_test_ffmpegwrapper.txt", rotation="10 MB")
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", ResourceWarning)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_concat_imported_video_files(
        self,
    ):
        """
        Test the concatenation of two imported video files
        Here we check the behavior of ffmpeg when concatenating two video files
        with different encodings
        """

        with WorkingFolderContext():
            # Here we have to reencode the videos first
            catrix_reloaded = await reencode_video(
                video_url=tests_medias.get_cat_video_path(),
                target_video_name="supercat_reencoded.mp4",
            )
            trainboy_reencoded = await reencode_video(
                video_url=tests_medias.get_test_transition_stones_trainboy_path(),
                target_video_name="trainboy_reencoded.mp4",
            )

            generated_vid_file = await concatenate_videos(
                video_file_paths=[catrix_reloaded, trainboy_reencoded],
                target_file_name="target.mp4",
                ratio_to_multiply_animations=1,
            )

            assert generated_vid_file == "target.mp4"
            assert os.path.exists(generated_vid_file)
            assert os.path.getsize(generated_vid_file) > 0

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_concatenate_videos__fps_mismatch__fails(self):
        with WorkingFolderContext():
            # Here we have to reencode the videos first
            catrix_reloaded = await reencode_video(
                video_url=tests_medias.get_cat_video_path(),
                target_video_name="supercat_reencoded.mp4",
                fps=24,
            )
            trainboy_reencoded = await reencode_video(
                video_url=tests_medias.get_test_transition_stones_trainboy_path(),
                target_video_name="trainboy_reencoded.mp4",
                fps=25,  # different FPS
            )

            with pytest.raises(
                ValueError, match="Cannot concatenate videos with different FPS"
            ):
                await concatenate_videos(
                    video_file_paths=[catrix_reloaded, trainboy_reencoded],
                    target_file_name="target.mp4",
                    ratio_to_multiply_animations=1,
                )

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_concat_generated_video_files(
        self,
    ):
        """
        Test the concatenation of two imported video files
        Here we check the behavior of ffmpeg when concatenating two video files
        with same encodings (as being provided by the same platform and model)
        """

        with WorkingFolderContext():
            generated_vid_file = await concatenate_videos(
                video_file_paths=[
                    tests_medias.get_generated_3s_forest_video_2_path(),
                    tests_medias.get_generated_3s_forest_video_1_path(),
                ],
                target_file_name="target.mp4",
                ratio_to_multiply_animations=1,
            )

            assert generated_vid_file == "target.mp4"
            assert os.path.exists(generated_vid_file)
            assert os.path.getsize(generated_vid_file) > 0

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_cut_video(
        self,
    ):
        """
        Test the capacity to cut video
        """
        with WorkingFolderContext():
            cutted_video = await cut_video(
                video_url=tests_medias.get_cat_video_path(),
                start_time=1,
                end_time=2,
            )
            logger.debug(
                "Cutting video, video size before cut: "
                + str(get_media_duration(tests_medias.get_cat_video_path()))
                + " and after cut: "
                + str(get_media_duration(cutted_video))
            )

            assert int(get_media_duration(cutted_video)) == 1

            cutted_video = await cut_video(
                video_url=tests_medias.get_haiper_video_path(),
                start_time=1,
                end_time=3,
            )

            logger.debug(
                "Cutting video, video size before cut: "
                + str(get_media_duration(tests_medias.get_cat_video_path()))
                + " and after cut: "
                + str(get_media_duration(cutted_video))
            )

            assert int(get_media_duration(cutted_video)) == 2

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_create_zoom_video(
        self,
    ):
        """
        Test the capacity to cut video
        """
        with WorkingFolderContext():
            zoomed_video = await create_zoom_video(
                image_url=tests_medias.get_test_prompt_image(),
                target_duration=5,
            )
            logger.debug(
                "Cutting video, initial video size : "
                + str(get_media_duration(zoomed_video))
            )

            assert int(get_media_duration(zoomed_video)) == 5

            zoomed_video = await create_zoom_video(
                image_url=tests_medias.get_test_prompt_image()
            )

            assert int(get_media_duration(zoomed_video)) == 3

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "video_path, target_dir",
        [
            (tests_medias.get_paris_video(), None),
            (tests_medias.get_paris_video(), "."),
            (tests_medias.get_paris_video(), "aFolder"),
        ],
    )
    async def test_extract_audio_from_video(self, video_path, target_dir):
        """
        Extract the audio and test its duration
        """
        with WorkingFolderContext() as wf:
            target_audio = await extract_audio_from_video(
                video_full_path=video_path,
                target_dir=target_dir,
            )
            logger.debug(
                "Extracting audio, video duration: "
                + str(get_media_duration(tests_medias.get_cat_video_path()))
                + " and audio duration: "
                + str(get_media_duration(target_audio))
            )
            assert math.isclose(
                get_media_duration(target_audio),
                get_media_duration(tests_medias.get_paris_video()),
                rel_tol=0.05,
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_audio_no_video(self):
        """
        Extract the audio and test its duration
        """
        with pytest.raises(ValueError):
            _ = await extract_audio_from_video(
                video_full_path=None,
                target_dir=None,
            )

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_generate_image_video(self):
        """
        Extract the audio and test its duration
        """
        with WorkingFolderContext():
            image_video = await generate_video_from_image(
                image_url=tests_medias.get_test_prompt_image(),
            )
            assert int(get_media_duration(image_video)) == 5
