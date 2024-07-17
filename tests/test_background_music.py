import os

import pytest
from loguru import logger

import warnings
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.common.context_managers import WorkingFolderContext

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestBackgroundMusic:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_background_music.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_background_music_from_empty_prompt(self):
        with WorkingFolderContext():
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )

            _ = ml_gw.generate_background_music_async(duration=3, prompt="")

    @pytest.mark.local_integration
    async def test_generate_background_music_from_short_prompt(self):
        with pytest.raises(TypeError):
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=True
            )
            _ = ml_gw.generate_background_music_async(duration="a")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_background_music_from_prompt(self):
        with WorkingFolderContext():
            ml_gw = ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )
            music_path = ml_gw.generate_background_music_async(
                duration=3, prompt=TEST_PROMPT
            )
            assert music_path, "There is no background music for the video"
            assert os.path.exists(music_path), "the generated music does not exists"
