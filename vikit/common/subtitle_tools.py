from copy import deepcopy

from pysrt import SubRipFile, SubRipTime


def trim_subtitles(
    subtitles: SubRipFile, start_time_sec: float, end_time_sec: float
) -> SubRipFile:
    """
    Trim the subtitles to the specified time range and shift their timing to begin
    at 0 seconds.

    Args:
        subtitles: The subtitles to preprocess.
        start_time_sec: The start time (in seconds) of the desired range.
        end_time_sec: The end time (in seconds) of the desired range.

    Returns:
        A `SubRipFile` object containing the trimmed subtitles. Possibly empty.
    """
    # Make a copy so we don't modify the original subtitles.
    processed = deepcopy(subtitles)

    # Only include subtitles that overlap with the requested time range.
    processed = processed.slice(
        starts_before={"seconds": end_time_sec},
        ends_after={"seconds": start_time_sec},
    )

    if len(processed) == 0:
        return processed

    # Adjust the first and last subtitle to fit within the requested time range.
    first_word = processed[0]
    first_word.start = max(first_word.start, SubRipTime(seconds=start_time_sec))
    last_word = processed[-1]
    last_word.end = min(last_word.end, SubRipTime(seconds=end_time_sec))

    # Shift subtitles to start from time = 0s.
    processed.shift(seconds=-start_time_sec)

    return processed
