import pytest
from loguru import logger

import warnings

from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo

warnings.simplefilter("ignore", category=ResourceWarning)
warnings.simplefilter("ignore", category=UserWarning)
logger.add("log_test_CI_prviders_health_checks.txt", rotation="10 MB")


class TestProvidersHealthChecks:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_haiper_provider_and_generate(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a fantastic day today")
            await video.build_async(
                build_settings=VideoBuildSettings(
                    test_mode=False, target_model_provider="haiper"
                )
            )
            assert video.media_url is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_stabilityai_provider_and_generate(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a fantastic day today")
            await video.build_async(
                build_settings=VideoBuildSettings(
                    test_mode=False, target_model_provider="stabilityai"
                )
            )
            assert video.media_url is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_videocrafter_provider_and_generate(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo("This is a fantastic day today")
            await video.build_async(
                build_settings=VideoBuildSettings(
                    test_mode=False, target_model_provider="videocrafter"
                )
            )
            assert video.media_url is not None
