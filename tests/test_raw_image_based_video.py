import os
import unittest
import pytest

from loguru import logger

import warnings

# from unittest.mock import patch, MagicMock, Mock
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from tests.tests_medias import get_test_prompt_image

TEST_PROMPT = get_test_prompt_image()


class TestImagePromptBasedVideo(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_raw_image_based_video.txt", rotation="10 MB")

    @pytest.mark.local_integration
    def test_get_title(self):
        with WorkingFolderContext():
            video_title = RawImageBasedVideo(
                raw_image_prompt=PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                )
                .create_prompt_from_image(TEST_PROMPT)
                ._image,
                title="test_image_prompt",
            ).get_title()
            logger.debug(f"Test get_title, video title: {video_title}")
            assert len(video_title) > 0  # we should have a file of at least 1 character

    @pytest.mark.local_integration
    def test_build_single_video_no_bg_music_without_subs(self):
        with WorkingFolderContext():

            pbvid = RawImageBasedVideo(
                raw_image_prompt=PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                )
                .create_prompt_from_image(TEST_PROMPT)
                ._image,
                title="test_image_prompt",
            )
            pbvid.build()

            assert pbvid.media_url, "media URL was not updated"
            assert pbvid._background_music_file_name is None
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    def test_build_single_video_no_bg_music_no_subtitles(self):
        with WorkingFolderContext():
            pbvid = RawImageBasedVideo(
                raw_image_prompt=PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                )
                .create_prompt_from_image(TEST_PROMPT)
                ._image,
                title="test_image_prompt",
            )
            pbvid.build(
                build_settings=VideoBuildSettings(include_audio_read_subtitles=False)
            )

            assert pbvid._background_music_file_name is None
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.local_integration
    def test_build_single_video_with_default_bg_music_no_subtitles(self):
        with WorkingFolderContext():
            pbvid = RawImageBasedVideo(
                raw_image_prompt=PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                )
                .create_prompt_from_image(TEST_PROMPT)
                ._image,
                title="test_image_prompt",
            )
            pbvid.build(
                build_settings=VideoBuildSettings(
                    include_audio_read_subtitles=False,
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=False
                    ),
                )
            )

            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"

    @pytest.mark.integration
    def test_build_single_video_with_generated_bg_music_no_subtitles(self):
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                include_audio_read_subtitles=False,
                music_building_context=MusicBuildingContext(
                    apply_background_music=True,
                    generate_background_music=True,
                ),
                test_mode=False,
            )

            pbvid = RawImageBasedVideo(
                raw_image_prompt=PromptFactory(
                    ml_gateway=ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway()
                )
                .create_prompt_from_image(TEST_PROMPT)
                ._image,
                title="test_image_prompt",
            )
            pbvid.build(
                build_settings=bld_settings,
            )
            assert pbvid.media_url, "media URL was not updated"
            assert os.path.exists(pbvid.media_url), "The generated video does not exist"
