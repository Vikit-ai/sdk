import warnings

import pytest
from loguru import logger
import pysrt

from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_raw_subs_from_text_prompt_extractor(self):
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        assert len(subs) > 0
        for sub in subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_heuristic_human_spoken_style_subs_from_text_prompt_extractor(
        self,
    ):
        # We  make sure that all subtitles are minimum of 7 seconds in order to be able to insert two videos inside
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        better_subs = sub_extractor.merge_short_subtitles(subs)

        for sub in better_subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None
            assert len(sub.text.split(" ")) >= 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reunion_island_prompt(self):
        with WorkingFolderContext():  # we work in the temp folder once for all the script
            gw = replicate_gateway.ReplicateGateway()
            test_prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(
                """A travel over Reunion Island, taken fomm birdview at 2000meters above 
                the ocean, flying over the volcano, the forest, the coast and the city of Saint Denis
                , then flying just over the roads in curvy mountain areas, and finally landing on the beach""",
                generate_recording=True,
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
