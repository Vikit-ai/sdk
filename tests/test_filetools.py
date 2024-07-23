import pytest
import warnings
import os

from loguru import logger

from vikit.common.file_tools import download_file
from vikit.common.context_managers import WorkingFolderContext
import tests.testing_medias as testing_medias


class TestFileTools:
    def setup():
        logger.add("log_test_Filetools.txt", rotation="10 MB")
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", ResourceWarning)

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_Download_with_local_file(
        self,
    ):
        """
        Test the download of a local file
        """

        with WorkingFolderContext():
            local_file = testing_medias.get_cat_video_path()
            downloaded_file = await download_file(local_file, "downloaded_cat.mp4")

            assert downloaded_file is not None
            assert downloaded_file == "downloaded_cat.mp4"
            assert downloaded_file != ""
            assert os.path.exists(downloaded_file)
            assert os.path.getsize(downloaded_file) > 0
