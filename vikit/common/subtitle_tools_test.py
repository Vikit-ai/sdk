from typing import List, Tuple

import pytest
from pysrt import SubRipFile, SubRipItem, SubRipTime

from vikit.common.subtitle_tools import trim_subtitles

TEST_SUBTITLES = [
    (0.0, 1.5, "word1"),
    (1.5, 3.0, "word2"),
    (3.0, 4.5, "word3"),
    (4.5, 6.0, "word4"),
]


@pytest.mark.unit
@pytest.mark.parametrize(
    "subtitles, start_time_sec, end_time_sec, expected_subtitles",
    [
        # Case 0: single word with no shift and no crop
        (TEST_SUBTITLES, 0.0, 1.5, [(0.0, 1.5, "word1")]),
        # Case 1: single word with crop and no shift
        (TEST_SUBTITLES, 0.1, 1.4, [(0.0, 1.3, "word1")]),
        # Case 2: single word with shift and no crop
        (TEST_SUBTITLES, 1.5, 3.0, [(0.0, 1.5, "word2")]),
        # Case 3: single word with shift and crop
        (TEST_SUBTITLES, 1.6, 2.9, [(0.0, 1.3, "word2")]),
        # Case 4: multiple words with shift and crop
        (TEST_SUBTITLES, 1.6, 4.4, [(0.0, 1.4, "word2"), (1.4, 2.8, "word3")]),
        # Case 5: no subtitles in range
        (TEST_SUBTITLES, 6.0, 7.0, []),
    ],
)
def test_trim_subtitles(subtitles, start_time_sec, end_time_sec, expected_subtitles):
    preprocessed = trim_subtitles(
        _create_sub_rip_file(subtitles), start_time_sec, end_time_sec
    )
    assert len(preprocessed) == len(expected_subtitles), (
        f"Wrong number of words. Expected: {len(expected_subtitles)}, "
        f"was: {len(preprocessed)}"
    )
    for idx, (
        expected_start_time_sec,
        expected_end_time_sec,
        expected_text,
    ) in enumerate(expected_subtitles):
        actual_start_time_sec = preprocessed[idx].start.ordinal / 1000.0
        assert actual_start_time_sec == expected_start_time_sec, (
            f"Wrong start time at index {idx}. Expected: {expected_start_time_sec}, "
            f"was: {actual_start_time_sec}"
        )
        actual_end_time_sec = preprocessed[idx].end.ordinal / 1000.0
        assert actual_end_time_sec == expected_end_time_sec, (
            f"Wrong end time at index {idx}. Expected: {expected_end_time_sec}, "
            f"was: {actual_end_time_sec}"
        )
        assert preprocessed[idx].text == expected_text, (
            f"Wrong word at index {idx}. Expected: {expected_text}, "
            f"was: {preprocessed[idx].text}"
        )


def _create_sub_rip_file(subtitles: List[Tuple[float, float, str]]) -> SubRipFile:
    sub_rip_file = SubRipFile()
    for index, (start_sec, end_sec, text) in enumerate(subtitles):
        sub_rip_file.append(
            SubRipItem(
                index=index,
                start=SubRipTime(seconds=start_sec),
                end=SubRipTime(seconds=end_sec),
                text=text,
            )
        )
    return sub_rip_file
