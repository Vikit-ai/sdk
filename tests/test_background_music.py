import os
import unittest
import pytest

import warnings
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.common.context_managers import WorkingFolderContext

TEST_PROMPT = "A group of stones in a forest, with symbols"


class TestBackgroundMusic(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self._ml_gw = (
            ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=False
            )
        )

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.integration
    def test_generate_background_music_from_empty_prompt(self):
        with WorkingFolderContext():
            _ = self._ml_gw.generate_background_music()

    def test_generate_background_music_from_short_prompt(self):
        with pytest.raises(TypeError):
            _ = self._ml_gw.generate_background_music(duration="a")

    @pytest.mark.integration
    def test_generate_background_music_from_prompt(self):
        with WorkingFolderContext():
            music_path = self._ml_gw.generate_background_music(
                duration=3, prompt=TEST_PROMPT
            )
            assert music_path, "There is no background music for the video"
            assert os.path.exists(music_path), "the generated music does not exists"
