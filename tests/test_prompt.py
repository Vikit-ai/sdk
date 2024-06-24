import unittest
import pytest
import warnings
from loguru import logger

from vikit.common.context_managers import WorkingFolderContext
from vikit.prompt.prompt_factory import PromptFactory
from tests.tests_medias import get_test_prompt_recording
from vikit.gateways import replicate_gateway as replicate_gateway

mp3_transcription = "ceci est un test rapide avec nma voix enregistrée pour faire un test"


class TestPrompt(unittest.TestCase):
            
    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_prompt.txt", rotation="10 MB")

    @pytest.mark.unit
    def test_generate_prompt_from_empty_prompt(self):
        with pytest.raises(ValueError):
            _ = PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_text(prompt_text=None)

    @pytest.mark.unit
    def test_generate_prompt_from_empty_audio(self):
        with pytest.raises(ValueError):
            _ = PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_audio_file(recorded_audio_prompt_path=None)

    @pytest.mark.integration
    def test_build_basic_audio_prompt_integration(self):
        with WorkingFolderContext():
            """
            here we check a prompt has been created sucessfully from an mp3 recording 
            """
            prompt = PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_audio_file(
                recorded_audio_prompt_path=get_test_prompt_recording())
            assert prompt is not None, "Prompt is None"
            assert prompt.text is not None, "Prompt text is None"
            assert prompt.audio_recording is not None, "Prompt sound recording path is None"
            assert prompt.audio_recording == get_test_prompt_recording()

    @pytest.mark.integration
    def test_build_basic_text_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            prompt = PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_text(prompt_text="This is a fake prompt")
            self.assertEqual(prompt.text, "This is a fake prompt")


    @pytest.mark.integration
    def test_reunion_island_prompt(self):
        with WorkingFolderContext():
            test_prompt = PromptFactory(ml_gateway=replicate_gateway.ReplicateGateway()).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
            )

            video = PromptBasedVideo(prompt=test_prompt)
            video.build(bld_sett)

            assert video.media_url is not None
            assert os.path.exists(video.media_url)
