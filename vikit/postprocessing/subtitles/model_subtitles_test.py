import pytest
from pydantic import ValidationError

from tests.medias.references_for_tests import (
    DEMAIN_DES_LAUBE_SRT,
    VIKIT_PITCH_MP4,
)
from vikit.postprocessing.subtitles.model import SubtitleConfig


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_video_path, output_video_name, subtitle_srt_path, font_size_px, "
    "highlight_opacity, text_color, highlight_color, bg_color, expected_error",
    [
        # Case : Empty input video path (ValidationError expected with specific message)
        (
            "",
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Input video path must be set",
        ),
        # Case : Empty output video name (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            "",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Output video name must be set",
        ),
        # Case : Empty subtitle file path (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            "",
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Subtitle SRT path must be set",
        ),
        # Case : Invalid output video name format (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            "output.txt",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Output video name must have one of the following formats",
        ),
        # Case : Invalid subtitle file format (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            "subtitle.txt",
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Subtitle SRT path must have the .srt extension",
        ),
        # Case : Negative font size (ValidationError expected due to invalid font size)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Font size px must be set",
        ),
        # Case : Highlight opacity greater than 1 (ValidationError expected due to invalid opacity)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            1.5,
            "white",
            "yellow",
            "(0,0,0)",
            "Value error, Font size px must be set",
        ),
        # Case : Invalid text_color format (ValidationError expected)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "invalid_color",
            "yellow",
            "(0,0,0)",
            "Value error, Text color is given invalid color format: invalid_color",
        ),
        # Case : Invalid highlight_color format (ValidationError expected)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "invalid_color",
            "(0,0,0)",
            "Value error, Highlight color is given invalid color format: invalid_color",
        ),
        # Case : Invalid bg_color format (ValidationError expected)
        (
            VIKIT_PITCH_MP4,
            "output.mp4",
            DEMAIN_DES_LAUBE_SRT,
            None,
            None,
            "white",
            "yellow",
            "invalid_color",
            "Value error, Bg color is given invalid color format: invalid_color",
        ),
    ],
)
def test_subtitle_config_invalid_parameters(
    input_video_path,
    output_video_name,
    subtitle_srt_path,
    font_size_px,
    highlight_opacity,
    text_color,
    highlight_color,
    bg_color,
    expected_error,
):
    with pytest.raises(ValidationError, match=expected_error):
        SubtitleConfig(
            input_video_path=input_video_path,
            output_video_name=output_video_name,
            subtitle_srt_path=subtitle_srt_path,
            font_size_px=font_size_px,
            highlight_opacity=highlight_opacity,
            text_color=text_color,
            highlight_color=highlight_color,
            bg_color=bg_color,
        )
