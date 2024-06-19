import unittest
import warnings

from loguru import logger

from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor

SAMPLE_PROMPT_TEXT = """A group of ancient, moss-covered stones come to life in an abandoned forest, revealing intricate carvings
and symbols. This is additional text to make sure we generate serveral subtitles. """

# Below are real integration tests, not to be run all the time


class TestSubtitlesExtrators(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    def test_extract_raw_subs_from_text_prompt_extractor(self):
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        assert len(subs) > 0
        for sub in subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None

    def test_extract_heuristic_human_spoken_style_subs_from_text_prompt_extractor(self):
        # We  make sure that all subtitles are minimum of 7 seconds in order to be able to insert two videos inside
        sub_extractor = TextPromptSubtitlesExtractor()
        subs = sub_extractor.extract_subtitles(SAMPLE_PROMPT_TEXT)
        assert subs is not None
        better_subs = sub_extractor.merge_short_subtitles(subs)

        for sub in better_subs:
            logger.debug(f"Sub: {sub.text}")
            assert sub.text is not None
            assert len(sub.text.split(" ")) >= 2
