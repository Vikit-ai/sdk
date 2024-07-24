import warnings

import pytest
from loguru import logger
import pysrt

from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.gateways import vikit_gateway
from vikit.common.context_managers import WorkingFolderContext
import tests.testing_tools as tools  # used to get a library of test prompts


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
            gw = vikit_gateway.VikitGateway()
            sub_extractor = RecordedPromptSubtitlesExtractor()
            subs: pysrt.SubRipFile = await sub_extractor.extract_subtitles_async(
                recorded_prompt_file_path=tools.test_prompt_library[
                    "moss_stones-train_boy"
                ].audio_recording,
                ml_models_gateway=gw,
            )

            for sub in subs:
                sub = pysrt.SubRipItem(sub)
                assert sub.text is not None
                logger.debug(f"Subtitle: {sub.text}")
