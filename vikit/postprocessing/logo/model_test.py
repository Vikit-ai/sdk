import pytest
from pydantic import ValidationError

from tests.medias.references_for_tests import (
    OUTPUT_VIDEO_WITH_LOGO_NAME,
    TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
    VIKIT_PITCH_MP4,
)
from vikit.postprocessing.logo.model import LogoConfig


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_video_path, output_video_name, logo, margin_pix, opacity, height_size_px, "
    "logo_height_percentage, position, expected_error",
    [
        # Case: Empty logo URL (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            "",
            None,
            None,
            None,
            None,
            None,
            "Value error, logo url must be set",
        ),
        # Case: Empty output video name (ValidationError expected with specific message)
        (
            VIKIT_PITCH_MP4,
            "",
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            None,
            None,
            "Value error, output_video_name must be set",
        ),
        # Case: Empty input video URL (ValidationError expected with specific message)
        (
            "",
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            None,
            None,
            "Value error, input_video_path must be set",
        ),
        # Case: Margin set to zero (ValidationError expected due to invalid margin)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            0,
            None,
            None,
            None,
            None,
            r"margin_pix\n.*Input should be greater than 0",
        ),
        # Case: Opacity greater than valid range (ValidationError expected due to
        # invalid opacity)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            1.5,
            None,
            None,
            "top_left",
            r"opacity\n.*Input should be less than or equal to 1",
        ),
        # Case: Height set to zero (ValidationError expected due to invalid height)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            0,
            None,
            None,
            r"height_size_px\n.*Input should be greater than 0.",
        ),
        # Case: Invalid logo height percentage (ValidationError expected due to invalid
        # percentage)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            0,
            None,
            r"logo_height_percentage\n.* Input should be greater than 0.",
        ),
        # Case: Invalid position value (ValidationError expected due to invalid
        # position)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            None,
            "center",
            r"position\n.*Input should be 'top_left', 'top_right', 'bottom_left' or "
            "'bottom_right'",
        ),
        # Case: Invalid input video path format (ValidationError expected with specific
        # message)
        (
            "video.txt",
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            None,
            None,
            "input_video_path must have one of the following formats",
        ),
        # Case: Invalid output video name format (ValidationError expected with specific
        # message)
        (
            VIKIT_PITCH_MP4,
            "output.txt",
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            None,
            None,
            None,
            None,
            None,
            "output_video_name must have one of the following formats",
        ),
        # Case: Invalid logo file format (ValidationError expected with specific
        # message)
        (
            VIKIT_PITCH_MP4,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            "logo.txt",
            None,
            None,
            None,
            None,
            None,
            "logo must have one of the following formats",
        ),
    ],
)
def test_logo_config_invalid_parameters(
    input_video_path,
    output_video_name,
    logo,
    margin_pix,
    opacity,
    height_size_px,
    logo_height_percentage,
    position,
    expected_error,
):
    with pytest.raises(ValidationError, match=expected_error):
        LogoConfig(
            input_video_path=input_video_path,
            output_video_name=output_video_name,
            logo=logo,
            margin_pix=margin_pix,
            opacity=opacity,
            height_size_px=height_size_px,
            logo_height_percentage=logo_height_percentage,
            position=position,
        )
