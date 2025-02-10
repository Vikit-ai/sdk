import os
import time

import pytest

from vikit.postprocessing.place_logo import VideoLogoOverlay
from vikit.common.context_managers import WorkingFolderContext

# List of test videos
TEST_CASES = [
    ( os.path.abspath("tests/medias/luma.mp4")),
    (os.path.abspath("tests/medias/vikit_pitch.mp4")),
]

LOGO_PATH =  os.path.abspath("tests/medias/transparent_vikit_logo_black.png")

@pytest.mark.asyncio
@pytest.mark.parametrize("video_path", TEST_CASES)
@pytest.mark.parametrize(
    "position", ["top_right", "top_left", "bottom_right", "bottom_left"]
)
@pytest.mark.local_integration
async def test_place_logo_on_video_valid_case(video_path, position):

    timestamp = int(time.time())
    video_basename = os.path.splitext(os.path.basename(video_path))[
        0
    ]  # Extract video name without extension
    output_path =  os.path.abspath(f"tmp/{video_basename}-test-{position}_{timestamp}.mp4")

    assert os.path.exists(video_path), f"Test video not found: {video_path}"
    assert os.path.exists(LOGO_PATH), f"Logo not found: {LOGO_PATH}"

    with WorkingFolderContext():
        overlay = VideoLogoOverlay(video_path, LOGO_PATH, output_path, "", position)
        await overlay.add_logo()

        assert os.path.exists(output_path), f"Output video was not generated: {output_path}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "video_path, logo_path, output_path, expected_exception",
    [
        (
            "no-video",
            LOGO_PATH,
            os.path.abspath("tests/medias/luma_with_logo.mp4"),
            FileNotFoundError,
        ),
        (
            TEST_CASES[0],
            "no-logo",
            os.path.abspath("tests/medias/luma_with_logo.mp4"),
            FileNotFoundError,
        ),
    ],
)
@pytest.mark.unit
async def test_place_logo_on_video_with_missing_files(
    video_path, logo_path, output_path, expected_exception
):
    overlay = VideoLogoOverlay(video_path, logo_path, output_path, "", "top_right")

    with pytest.raises(expected_exception):
        await overlay.add_logo()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_place_logo_on_video_with_no_output_video():
    video_path = TEST_CASES[0]
    output_path = ""  # No output path provided

    assert os.path.exists(video_path), f"Test video not found: {video_path}"
    assert os.path.exists(LOGO_PATH), f"Logo not found: {LOGO_PATH}"

    # Create the VideoLogoOverlay instance and expect an exception to be raised
    overlay = VideoLogoOverlay(video_path, LOGO_PATH, output_path, "", "top_right")

    # Expecting ValueError because output_path is empty
    with pytest.raises(ValueError, match="Output video path must be provided."):
        await overlay.add_logo()
