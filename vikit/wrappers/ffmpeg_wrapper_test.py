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
import subprocess

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
    has_audio_track,
    get_video_resolution,
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


def _create_dummy_video(
    file_path: str,
    duration: int,
    with_audio: bool,
    width: int = 640,
    height: int = 480,
    rate: int = 24,
):
    """
    Helper function to create a dummy video file using ffmpeg.
    """
    video_cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        f"testsrc=duration={duration}:size={width}x{height}:rate={rate}",
    ]

    if with_audio:
        audio_cmd = [
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
        ]
        cmd = video_cmd + audio_cmd
        cmd.extend(["-map", "0:v", "-map", "1:a"])
    else:
        cmd = video_cmd
        cmd.extend(["-map", "0:v"])

    cmd.extend(
        [
            "-y",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            str(file_path),
        ]
    )

    logger.debug(f"Running command to create dummy video: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    logger.debug(f"Successfully created dummy video: {file_path}")


@pytest.mark.local_integration
@pytest.mark.asyncio
async def test_concatenate_mixed_audio_videos():
    """
    Test the concatenation of a video with audio and a video without audio.
    It ensures the final video correctly contains an audio track.
    """
    with WorkingFolderContext() as wf:
        video_with_audio_path = "video_with_audio.mp4"
        video_without_audio_path = "video_without_audio.mp4"
        output_path = "concatenated_video.mp4"

        duration1 = 3
        duration2 = 2
        total_duration = duration1 + duration2

        # 1. Setup
        _create_dummy_video(video_with_audio_path, duration=duration1, with_audio=True)
        _create_dummy_video(
            video_without_audio_path, duration=duration2, with_audio=False
        )

        assert os.path.exists(video_with_audio_path)
        assert os.path.exists(video_without_audio_path)

        # 2. Execute
        await concatenate_videos(
            video_file_paths=[video_with_audio_path, video_without_audio_path],
            target_file_name=output_path,
            fps=24,
        )

        # 3. Assert
        assert os.path.exists(output_path), "The output video file was not created."

        output_duration = get_media_duration(output_path)
        assert output_duration == pytest.approx(total_duration, abs=0.5), (
            f"Expected duration ~{total_duration}s, but got {output_duration:.2f}s."
        )

        assert has_audio_track(output_path), (
            "The concatenated video should have an audio track, but it doesn't."
        )

        output_width, output_height = get_video_resolution(output_path)
        assert output_width == 640
        assert output_height == 480

        logger.info("Test for mixed audio concatenation passed successfully.")
