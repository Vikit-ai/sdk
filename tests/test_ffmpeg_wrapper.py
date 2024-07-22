import pytest
import warnings
import os

from loguru import logger

from vikit.wrappers.ffmpeg_wrapper import concatenate_videos, reencode_video
from vikit.common.context_managers import WorkingFolderContext
import tests.tests_medias as tests_medias


class TestFFMPEGWrapper:
    def setup():
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
            concat_file_name = "concatenate.txt"
            # Here we have to reencode the videos first
            catrix_reloaded = await reencode_video(
                video_url=tests_medias.get_cat_video_path(),
                target_video_name="supercat_reencoded.mp4",
            )
            trainboy_reencoded = await reencode_video(
                video_url=tests_medias.get_test_transition_stones_trainboy_path(),
                target_video_name="trainboy_reencoded.mp4",
            )

            with open(concat_file_name, "w") as f:
                f.write(f"file {catrix_reloaded}\n")
                f.write(f"file {trainboy_reencoded}\n")

            generated_vid_file = await concatenate_videos(
                input_file=concat_file_name,
                target_file_name="target.mp4",
                ratioToMultiplyAnimations=1,
            )

            assert generated_vid_file is not None
            assert generated_vid_file == "target.mp4"
            assert generated_vid_file != ""
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
            concat_file_name = "concatenate.txt"
            with open(concat_file_name, "w") as f:
                f.write(f"file {tests_medias.get_generated_3s_forest_video_2_path()}\n")
                f.write(f"file {tests_medias.get_generated_3s_forest_video_1_path()}\n")

            generated_vid_file = await concatenate_videos(
                input_file=concat_file_name,
                target_file_name="target.mp4",
                ratioToMultiplyAnimations=1,
            )

            assert generated_vid_file is not None
            assert generated_vid_file == "target.mp4"
            assert generated_vid_file != ""
            assert os.path.exists(generated_vid_file)
            assert os.path.getsize(generated_vid_file) > 0
