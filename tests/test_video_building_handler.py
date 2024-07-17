import warnings
import pytest
from loguru import logger

from vikit.video.building.handlers.videogen_handler import (
    VideoBuildingHandlerGenerateFomApi,
)
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video_build_settings import VideoBuildSettings


class TestVideoBuildingHandler:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_video_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_VideoBuildingHandlerGenerateFomApi(self):
        api_handler = VideoBuildingHandlerGenerateFomApi()
        vid = RawTextBasedVideo("test")
        vid.build_settings = VideoBuildSettings()
        vid = await vid.prepare_build(build_settings=vid.build_settings)
        video_built = await api_handler.execute_async(video=vid)
        assert video_built is not None, "Video built should not be None"
        assert (
            api_handler.is_supporting_async_mode()
        ), f"This handler should support async, but it does not: {api_handler}"
