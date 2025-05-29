import os
from tempfile import NamedTemporaryFile

import pytest
from moviepy.video.io.VideoFileClip import VideoFileClip

from tests.medias.references_for_tests import (
    MARCHAND_360P_MP4,
    MARCHAND_CHUNK_SRT,
    QUOTIDIEN_360P_MP4,
    QUOTIDIEN_CHUNK_SRT,
    RANCHO_FONT,
)
from vikit.common.context_managers import WorkingFolderContext
from vikit.postprocessing.subtitles.simple_video_subtitle_renderer import (
    SimpleVideoSubtitleRenderer,
)


def valid_init_kwargs(remove: list[str] = [], update: dict[str, any] = {}):
    valid_kwargs = {
        "font_path": RANCHO_FONT,
        "font_size_pt": 24,
        "margin_bottom_ratio": 0.20,
        "margin_h_ratio": 0.10,
    }
    return {k: v for k, v in valid_kwargs.items() if k not in remove} | update


def valid_render_kwargs(remove: list[str] = [], update: dict[str, any] = {}):
    valid_kwargs = {
        "input_video_path": MARCHAND_360P_MP4,
        "subtitle_srt_filepath": MARCHAND_CHUNK_SRT,
        "output_video_path": "output.mp4",
        "text_color": "white",
        "highlight_color": (0, 0, 0),
        "highlight_opacity": 0.8,
    }
    return {k: v for k, v in valid_kwargs.items() if k not in remove} | update


@pytest.mark.local_integration
@pytest.mark.parametrize(
    "video_path, subtitle_path",
    [
        (MARCHAND_360P_MP4, MARCHAND_CHUNK_SRT),
        (QUOTIDIEN_360P_MP4, QUOTIDIEN_CHUNK_SRT),
    ],
)
def test_create_video_subtitles__valid_input__succeeds(video_path, subtitle_path):
    with WorkingFolderContext():
        render_kwargs = valid_render_kwargs(
            update={
                "input_video_path": video_path,
                "subtitle_srt_filepath": subtitle_path,
            }
        )

        subtitle_renderer = SimpleVideoSubtitleRenderer(**valid_init_kwargs())
        subtitle_renderer.add_subtitles_to_video(**render_kwargs)

        output_video_path = render_kwargs["output_video_path"]
        assert os.path.exists(output_video_path), (
            f"Output video file was not created: {os.path.abspath(output_video_path)}"
        )
        assert (
            VideoFileClip(output_video_path).duration
            >= VideoFileClip(video_path).duration
        ), "Output video duration is incorrect"


@pytest.mark.local_integration
def test_create_video_subtitles__missing_optional_args__succeeds():
    with WorkingFolderContext():
        init_kwargs = valid_init_kwargs(
            remove=["font_path", "font_size_pt", "margin_bottom_ratio"]
        )
        subtitle_renderer = SimpleVideoSubtitleRenderer(**init_kwargs)

        render_kwargs = valid_render_kwargs(
            remove=["text_color", "highlight_color", "highlight_opacity"]
        )
        subtitle_renderer.add_subtitles_to_video(**render_kwargs)

        output_video_path = render_kwargs["output_video_path"]
        assert os.path.exists(output_video_path), (
            f"Output video file was not created: {os.path.abspath(output_video_path)}"
        )

        input_video_path = render_kwargs["input_video_path"]
        assert (
            VideoFileClip(output_video_path).duration
            >= VideoFileClip(input_video_path).duration
        ), "Output video duration is incorrect"


@pytest.mark.local_integration
@pytest.mark.parametrize(
    "init_kwargs, render_kwargs, expected_exception, expected_message",
    [
        (
            valid_init_kwargs(update={"font_path": "unknown.ttf"}),
            valid_render_kwargs(),
            FileNotFoundError,
            "unknown.ttf",
        ),
        (
            valid_init_kwargs(update={"font_size_pt": 0}),
            valid_render_kwargs(),
            ValueError,
            r"font_size_pt \(0\) must be > 0",
        ),
        (
            valid_init_kwargs(update={"margin_bottom_ratio": -0.1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_bottom_ratio \(-0.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(update={"margin_bottom_ratio": 1.1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_bottom_ratio \(1.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(update={"margin_h_ratio": -0.1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_h_ratio \(-0.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(update={"margin_h_ratio": 1.1}),
            valid_render_kwargs(),
            ValueError,
            r"margin_h_ratio \(1.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"input_video_path": "unknown.mp4"}),
            FileNotFoundError,
            "unknown.mp4",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(
                update={"output_video_path": "/unknown-path/video.mp4"}
            ),
            FileNotFoundError,
            "/unknown-path",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"subtitle_srt_filepath": "unknown.srt"}),
            FileNotFoundError,
            "unknown.srt",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"text_color": "unknown-color"}),
            ValueError,
            "Invalid color format: unknown-color",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"highlight_color": "unknown-color"}),
            ValueError,
            "Invalid color format: unknown-color",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"highlight_opacity": -0.1}),
            ValueError,
            r"bg_opacity \(-0.1\) must be in the range \[0, 1\]",
        ),
        (
            valid_init_kwargs(),
            valid_render_kwargs(update={"highlight_opacity": 1.1}),
            ValueError,
            r"bg_opacity \(1.1\) must be in the range \[0, 1\]",
        ),
    ],
)
def test_create_video_subtitles__invalid_arg__fails(
    init_kwargs, render_kwargs, expected_exception, expected_message
):
    with pytest.raises(expected_exception, match=expected_message):
        subtitle_renderer = SimpleVideoSubtitleRenderer(**init_kwargs)
        subtitle_renderer.add_subtitles_to_video(**render_kwargs)


@pytest.mark.local_integration
def test_create_video_subtitles__invalid_srt_file__fails():
    with NamedTemporaryFile(mode="w", delete=True) as srt_file:
        srt_file.write("Invalid SRT content")
        srt_file.flush()

        subtitle_renderer = SimpleVideoSubtitleRenderer(**valid_init_kwargs())
        with pytest.raises(ValueError, match="Failed to parse subtitle file"):
            render_kwargs = valid_render_kwargs(
                update={"subtitle_srt_filepath": srt_file.name}
            )
            subtitle_renderer.add_subtitles_to_video(**render_kwargs)
