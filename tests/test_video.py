import os
import warnings

import pytest
from loguru import logger

from vikit.video.imported_video import ImportedVideo
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.common.context_managers import WorkingFolderContext
import tests.tests_tools as tools  # used to get a library of test prompts


TESTS_MEDIA_FOLDER = "medias/"
SMALL_VIDEO_CHAT_FILE = "chat_video_super8.mp4"


def get_cat():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    media_dir = os.path.join(dir_path, TESTS_MEDIA_FOLDER)
    return os.path.join(media_dir, SMALL_VIDEO_CHAT_FILE)


class TestVideo:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        logger.add("log_test_video.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_first_frame_as_image_path_with_non_generated_video(self):
        await PromptBasedVideo(
            tools.test_prompt_library["moss_stones-train_boy"]
        ).get_first_frame_as_image()

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_last_frame_as_image_path_with_non_generated_video(self):
        with pytest.raises(AssertionError):
            await PromptBasedVideo(
                tools.test_prompt_library["moss_stones-train_boy"]
            ).get_last_frame_as_image()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_duration(self):
        with WorkingFolderContext():
            with pytest.raises(
                ValueError
            ):  # As the video is not generated, we should raise an error
                PromptBasedVideo(
                    tools.test_prompt_library["moss_stones-train_boy"]
                ).get_duration()

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_first_frame_as_image_path_with_sample_video(self):
        sample_video_path = os.path.join(get_cat())
        with WorkingFolderContext():
            logger.debug(f"sample_video_path : {sample_video_path}")
            video = ImportedVideo(video_file_path=sample_video_path)
            image_path = await video.get_first_frame_as_image()

            assert image_path is not None
            assert len(image_path) > 0
            assert os.path.exists(image_path)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_get_last_frame_as_image_path_with_sample_video(self):
        with WorkingFolderContext():
            video = ImportedVideo(video_file_path=get_cat())
            image_path = await video.get_last_frame_as_image()

            assert image_path is not None
            assert image_path.__len__() > 0
            assert os.path.exists(image_path)
