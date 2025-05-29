import os
import time

import pytest
from pydantic import ValidationError

from tests.medias.references_for_tests import (
    IMAGE_SVG,
    LUMA_MP4,
    OUTPUT_VIDEO_WITH_LOGO_NAME,
    TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
    VIKIT_PITCH_MP4,
    WHITE_BACKGROUND_VIKIT_LOGO_BLACK_PNG,
)
from vikit.common.context_managers import WorkingFolderContext
from vikit.postprocessing.logo.model import LogoConfig
from vikit.postprocessing.logo.place_logo import VideoLogoOverlayer


@pytest.mark.asyncio
@pytest.mark.parametrize("video_path", [LUMA_MP4, VIKIT_PITCH_MP4])
@pytest.mark.parametrize(
    "position", ["top_right", "top_left", "bottom_right", "bottom_left"]
)
@pytest.mark.local_integration
async def test_place_logo_on_video_valid_case(video_path, position):
    with WorkingFolderContext():
        timestamp = int(time.time())
        video_basename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = f"{video_basename}-test-{position}_{timestamp}.mp4"

        assert os.path.exists(video_path), f"Test video not found: {video_path}"
        assert os.path.exists(TRANSPARENT_VIKIT_LOGO_BLACK_PNG), (
            f"Logo not found: {TRANSPARENT_VIKIT_LOGO_BLACK_PNG}"
        )

        logo_config = LogoConfig(
            input_video_path=video_path,
            output_video_name=output_path,
            logo=TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            position=position,
            height_size_px=50,
            logo_height_percentage=10,
            margin_pix=10,
        )

        logo_overlayer = VideoLogoOverlayer(logo_config)
        await logo_overlayer.overlay_logo()

        assert os.path.exists(output_path), (
            f"Output video was not generated: {output_path}"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "video_path, logo_path, output_path, expected_exception, expected_error_msg",
    [
        (
            "",
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            OUTPUT_VIDEO_WITH_LOGO_NAME,
            ValidationError,
            "input_video_path",
        ),
        (LUMA_MP4, "", OUTPUT_VIDEO_WITH_LOGO_NAME, ValidationError, "logo"),
        (
            LUMA_MP4,
            TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            "",
            ValidationError,
            "output_video_name",
        ),
    ],
)
@pytest.mark.unit
async def test_place_logo_on_video_with_missing_files(
    video_path, logo_path, output_path, expected_exception, expected_error_msg
):
    with pytest.raises(expected_exception) as exc_info:
        logo_config = LogoConfig(
            input_video_path=video_path,
            output_video_name=output_path,
            logo=logo_path,
            position="top_left",
            height_size_px=50,
            logo_height_percentage=10,
            margin_pix=10,
        )

        overlay = VideoLogoOverlayer(logo_config)
        await overlay.overlay_logo()

    assert expected_error_msg in str(exc_info.value), (
        f"Unexpected error: {exc_info.value}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "output_sub, opacity",
    [
        ("zero-nine-opacity", 0.9),
        ("zero-seven-opacity", 0.7),
        ("zero-five-opacity", 0.5),
    ],
)
@pytest.mark.unit
async def test_place_logo_with_different_opacities(output_sub, opacity):
    with WorkingFolderContext():
        video_basename = os.path.splitext(os.path.basename(LUMA_MP4))[0]
        output_path = f"{video_basename}-test-{output_sub}.mp4"

        logo_config = LogoConfig(
            input_video_path=LUMA_MP4,
            output_video_name=output_path,
            logo=WHITE_BACKGROUND_VIKIT_LOGO_BLACK_PNG,
            position="top_right",
            height_size_px=50,
            logo_height_percentage=10,
            margin_pix=10,
            opacity=opacity,
        )

        logo_overlayer = VideoLogoOverlayer(logo_config)
        await logo_overlayer.overlay_logo()

        assert os.path.exists(output_path), (
            f"Output video was not generated: {output_path}"
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_overlay_logo_with_png_conversion():
    with WorkingFolderContext():
        video_basename = os.path.splitext(os.path.basename(LUMA_MP4))[0]
        output_path = f"{video_basename}-test.mp4"

        logo_config = LogoConfig(
            input_video_path=LUMA_MP4,
            output_video_name=output_path,
            logo=TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
            position="top_right",
            height_size_px=50,
            logo_height_percentage=10,
            margin_pix=10,
            opacity=1,
        )

        logo_overlayer = VideoLogoOverlayer(logo_config)
        await logo_overlayer.overlay_logo()

        assert os.path.exists(output_path), (
            f"Output video was not generated: {output_path}"
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_overlay_logo_with_svg_conversion():
    with WorkingFolderContext():
        video_basename = os.path.splitext(os.path.basename(LUMA_MP4))[0]
        output_path = f"{video_basename}-test.mp4"

        logo_config = LogoConfig(
            input_video_path=LUMA_MP4,
            output_video_name=output_path,
            logo=IMAGE_SVG,
            position="top_right",
            height_size_px=50,
            logo_height_percentage=10,
            margin_pix=10,
            opacity=1,
        )

        logo_overlayer = VideoLogoOverlayer(logo_config)
        await logo_overlayer.overlay_logo()

        assert os.path.exists(output_path), (
            f"Output video was not generated: {output_path}"
        )
