import pytest
import unittest
import warnings
from loguru import logger

from vikit.video_building.handlers.videogen_handler import (
    VideoBuildingHandlerGenerateFomApi,
)
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video_build_settings import VideoBuildSettings


class TestVideoBuildingHandler(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt.txt", rotation="10 MB")

    @pytest.mark.unit
    def test_VideoBuildingHandlerGenerateFomApi(self):
        api_handler = VideoBuildingHandlerGenerateFomApi()
        vid = RawTextBasedVideo("test")
        vid.build_settings = VideoBuildSettings()
        video_built = api_handler.execute(video=vid)
        assert video_built is not None, "Video built should not be None"
        assert api_handler.supports_async, "This handler should support async"
