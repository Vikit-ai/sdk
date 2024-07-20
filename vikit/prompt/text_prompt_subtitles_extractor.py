import pysrt

from vikit.prompt.subtitle_extractor import SubtitleExtractor
import vikit.common.config as config


class TextPromptSubtitlesExtractor(SubtitleExtractor):
    """
    A class to extract subtitles from a text,

    We do use an heuristic, so it is not as good
    as creating a recording and getting the prompts from LLMs in the right language
    but it is a good start and it goes faster than the other way around.

    So  here we just split the text prompt into words and consider each word takes roughly
    x seconds to pronounce. All these are set in config files

    Here we don't need to rebuild a full srt file as with recorded prompts

    """

    def extract_subtitles(self, text) -> list[pysrt.SubRipItem]:
        """
        Generate subtitles from a text prompt

        Args:
            text: The text prompt

        Returns:
            A list of subtitles generated from the text prompt as a list of pysrt.SubRipItem
        """
        assert text is not None, "The text prompt is not provided"
        words = text.split(" ")
        subs = []
        i = 0
        nb_words_per_sub = config.get_nb_words_per_subtitle()
        sec_per_word = config.get_seconds_per_word()
        while i < len(words):
            sub = pysrt.SubRipItem()
            sub.index = i
            sub.text = " ".join(words[i : i + nb_words_per_sub])
            sub.start.seconds = i * sec_per_word
            sub.end.seconds = (i + nb_words_per_sub) * sec_per_word
            subs.append(sub)
            i += config.get_nb_words_per_subtitle()
        return subs
