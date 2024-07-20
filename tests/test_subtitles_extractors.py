import warnings

import pytest
from loguru import logger
import pysrt

from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.prompt.prompt_factory import PromptFactory
from vikit.gateways import replicate_gateway as replicate_gateway
from vikit.common.context_managers import WorkingFolderContext


SAMPLE_PROMPT_TEXT = """A group of ancient, moss-covered stones come to life in an abandoned forest, revealing intricate carvings
and symbols. This is additional text to make sure we generate serveral subtitles. """

# Below are real integration tests, not to be run all the time


class TestSubtitlesExtrators:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_subtitles_extractors.txt", rotation="10 MB")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reunion_island_prompt(self):
        with WorkingFolderContext():
            gw = replicate_gateway.ReplicateGateway()
            test_prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
            )

            sub_extractor = RecordedPromptSubtitlesExtractor()
            subs: pysrt.SubRipFile = await sub_extractor.extract_subtitles_async(
                recorded_prompt_file_path=test_prompt.recorded_audio_prompt_path,
                ml_models_gateway=gw,
            )

            for sub in subs:
                sub = pysrt.SubRipItem(sub)
                assert sub.text is not None
                assert sub.text != ""
                logger.trace(f"Subtitle: {sub.text}")
