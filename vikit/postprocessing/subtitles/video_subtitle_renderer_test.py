import os
from math import isclose
from typing import List, Tuple

import pytest
from moviepy.video.io.VideoFileClip import VideoFileClip
from pysrt import SubRipFile, SubRipItem, SubRipTime

from tests.medias.references_for_tests import (
    MARCHAND_360P_MP4,
    MARCHAND_CHUNK_SRT,
    QUOTIDIEN_360P_MP4,
    QUOTIDIEN_CHUNK_SRT,
    RANCHO_FONT,
)
from vikit.common.context_managers import WorkingFolderContext
from vikit.postprocessing.subtitles.video_subtitle_renderer import (
    VideoSubtitleRenderer,
    _convert_color_to_rgb,
    _normalize_color,
    _split_subtitles_by_group,
)


def valid_init_kwargs(remove: list[str] = [], update: dict[str, any] = {}):
    valid_kwargs = {
        "subtitle_style": "highlight_spoken_word",
        "font_path": RANCHO_FONT,
        "font_size_pt": 24,
        "text_color": "white",
        "highlight_color": "yellow",
        "bg_color": "black",
        "bg_opacity": 0.8,
        "margin_bottom_px": 100,
        "margin_h_px": 10,
    }
    return {k: v for k, v in valid_kwargs.items() if k not in remove} | update


def valid_render_kwargs(remove: list[str] = [], update: dict[str, any] = {}):
    valid_kwargs = {
        "src_video_path": MARCHAND_360P_MP4,
        "dst_video_path": "output.mp4",
        "subtitles": SubRipFile.open(MARCHAND_CHUNK_SRT),
    }
    return {k: v for k, v in valid_kwargs.items() if k not in remove} | update


TEST_SUBTITLES = [
    (0.0, 1.5, "word1"),
    (1.5, 3.0, "word2"),
    (3.0, 4.5, "word3"),
    (4.5, 6.0, "word4"),
]


@pytest.mark.local_integration
@pytest.mark.parametrize(
    "src_video_path, subtitles_srt_path",
    [
        (MARCHAND_360P_MP4, MARCHAND_CHUNK_SRT),
        (QUOTIDIEN_360P_MP4, QUOTIDIEN_CHUNK_SRT),
    ],
)
@pytest.mark.parametrize(
    "subtitle_style",
    [
        "static_block",
        "highlight_spoken_word",
        "highlight_spoken_sentence",
        "place_words",
    ],
)
def test_render_subtitles__valid_input(
    src_video_path, subtitles_srt_path, subtitle_style
):
    with WorkingFolderContext():
        init_kwargs = valid_init_kwargs(update={"subtitle_style": subtitle_style})
        renderer = VideoSubtitleRenderer(**init_kwargs)

        dst_video_path = "output.mp4"
        renderer.render(
            src_video_path,
            dst_video_path,
            SubRipFile.open(subtitles_srt_path),
        )

        assert os.path.exists(dst_video_path), (
            f"Output video file was not created: {os.path.abspath(dst_video_path)}"
        )

        with VideoFileClip(src_video_path) as src_video:
            with VideoFileClip(dst_video_path) as dst_video:
                assert isclose(src_video.duration, dst_video.duration, abs_tol=0.1), (
                    f"Wrong output video duration. Expected: "
                    f"{src_video.duration}s ± 0.1, was: {dst_video.duration}s"
                )


@pytest.mark.unit
@pytest.mark.parametrize(
    "init_kwargs, render_kwargs, expected_exception, expected_message",
    [
        (
            valid_init_kwargs(update={"subtitle_style": "unknown-style"}),
            valid_render_kwargs(),
            ValueError,
            r"subtitle_style \(unknown-style\) must be one of \(.*\)",
        ),
        (
            valid_init_kwargs(update={"font_path": "unknown.ttf"}),
            valid_render_kwargs(),
            FileNotFoundError,
            "unknown.ttf",
        ),
        (
            valid_init_kwargs(update={"font_size_pt": -1}),
            valid_render_kwargs(),
            ValueError,
            r"font_size_pt \(-1\) must be > 0",
        ),
        (
            valid_init_kwargs(update={"text_color": "invalid-color"}),
            valid_render_kwargs(),
            ValueError,
            "Invalid color format: invalid-color",
        ),
        (
            valid_init_kwargs(update={"highlight_color": "invalid-color"}),
            valid_render_kwargs(),
            ValueError,
            "Invalid color format: invalid-color",
        ),
        (
            valid_init_kwargs(update={"bg_color": "invalid-color"}),
            valid_render_kwargs(),
            ValueError,
            "Invalid color format: invalid-color",
        ),
        (
            valid_init_kwargs(update={"bg_opacity": -0.1}),
            valid_render_kwargs(),
            ValueError,
            r"bg_opacity \(-0.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(update={"bg_opacity": 1.1}),
            valid_render_kwargs(),
            ValueError,
            r"bg_opacity \(1.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(update={"margin_bottom_px": -1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_bottom_px \(-1\) must be in the range \[0, 640\]",
        ),
        (
            valid_init_kwargs(update={"margin_bottom_px": 641}),
            valid_render_kwargs(),
            ValueError,
            r"margin_bottom_px \(641\) must be in the range \[0, 640\]",
        ),
        (
            valid_init_kwargs(update={"margin_h_px": -1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_h_px \(-1\) must be in the range \[0, 180\]",
        ),
        (
            valid_init_kwargs(update={"margin_h_px": 181}),
            valid_render_kwargs(),
            ValueError,
            r"margin_h_px \(181\) must be in the range \[0, 180\]",
        ),
    ],
)
def test_init_renderer__invalid_arg__fails(
    init_kwargs, render_kwargs, expected_exception, expected_message
):
    with pytest.raises(expected_exception, match=expected_message):
        renderer = VideoSubtitleRenderer(**init_kwargs)
        renderer.render(**render_kwargs)


@pytest.mark.local_integration
def test_render_subtitles__invalid_params__no_subtitles_in_range():
    with WorkingFolderContext():
        src_video_path = MARCHAND_360P_MP4
        with VideoFileClip(src_video_path) as src_video:
            src_video_duration = src_video.duration

        subtitles = _create_sub_rip_file(
            [
                (src_video_duration, src_video_duration + 1.5, "word1"),
                (src_video_duration + 1.5, src_video_duration + 3.0, "word2"),
            ]
        )

        renderer = VideoSubtitleRenderer(**valid_init_kwargs())
        with pytest.raises(
            ValueError,
            match=(
                "No subtitles found in the specified time range: "
                rf"\[0s, {src_video_duration}s\]"
            ),
        ):
            renderer.render(src_video_path, "output.mp4", subtitles)


@pytest.mark.unit
@pytest.mark.parametrize(
    "color, expected_value",
    [
        ((10, 20, 30), "rgb(10, 20, 30)"),
        ((10, 20, 30, 0.4), "rgba(10, 20, 30, 0.4)"),
        ("#123", "#123"),
        ("#123456", "#123456"),
        ("#fafafa", "#fafafa"),
        ("#FAFAFA", "#FAFAFA"),
        ("rgb(1, 2, 3)", "rgb(1, 2, 3)"),
        ("white", "white"),
    ],
)
def test_normalize_color(color, expected_value):
    actual_value = _normalize_color(color)
    assert actual_value == expected_value, (
        f"Expected: {expected_value}, was: {actual_value}"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "color, expected_value",
    [
        ("transparent", (0, 0, 0, 0)),
        ("red", (255, 0, 0)),
        ("#0a0b0c", (10, 11, 12)),
        ("rgb(1, 2, 3)", (1, 2, 3)),
    ],
)
def test_convert_color_to_rgb(color, expected_value):
    actual_value = _convert_color_to_rgb(color)
    assert actual_value == expected_value, (
        f"Expected: {expected_value}, was: {actual_value}"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "subtitles, group_duration_sec, expected_group_count",
    [
        (TEST_SUBTITLES, 1.5, 4),
        (TEST_SUBTITLES, 3.0, 2),
        (TEST_SUBTITLES, 6.0, 1),
    ],
)
def test_split_subtitles_by_group(subtitles, group_duration_sec, expected_group_count):
    word_groups = list(
        _split_subtitles_by_group(_create_sub_rip_file(subtitles), group_duration_sec)
    )

    assert len(word_groups) == expected_group_count, (
        f"Wrong number of groups. Expected: {expected_group_count}, "
        f"was: {len(word_groups)}"
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
