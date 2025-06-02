from typing import Tuple

import numpy as np
import pytest
from moviepy.editor import ImageClip, VideoClip, VideoFileClip

from tests.medias.references_for_tests import LUMA_MP4
from vikit.common.context_managers import WorkingFolderContext
from vikit.common.video_tools import resize_video_clip, write_videofile


@pytest.mark.local_integration
def test_write_videofile():
    with WorkingFolderContext():
        original_video = VideoFileClip(LUMA_MP4, fps_source="fps")
        write_videofile(original_video, "test.mp4", fps=original_video.fps)
        written_video = VideoFileClip("test.mp4", fps_source="fps")

        assert original_video.fps == written_video.fps, (
            f"expected fps to be {original_video.fps} but was {written_video.fps}"
        )
        assert original_video.duration == written_video.duration, (
            f"expected duration to be {original_video.duration} but was "
            f"{written_video.duration}"
        )
        assert original_video.size == written_video.size, (
            f"expected size to be {original_video.size} but was {written_video.size}"
        )

    fps = original_video.fps
    frame_count = int(original_video.duration * fps)
    for frame_idx in range(frame_count):
        time = frame_idx / fps
        original_frame = original_video.get_frame(time)
        written_frame = original_video.get_frame(time)

        assert np.array_equal(original_frame, written_frame), (
            "frame mismatch at time={time}"
        )


@pytest.mark.unit
@pytest.mark.parametrize(
    "original_size, short_edge_length_px, expected_size",
    [
        ((100, 100), 360, (360, 360)),  # 1:1, size increase
        ((240, 320), 360, (360, 480)),  # 3:4, size increase
        ((320, 240), 360, (480, 360)),  # 4:3, size increase
        ((270, 480), 360, (360, 640)),  # 9:16, size increase
        ((480, 270), 360, (640, 360)),  # 16:9, size increase
        ((400, 400), 360, (360, 360)),  # 1:1, size decrease
        ((420, 560), 360, (360, 480)),  # 3:4, size decrease
        ((560, 420), 360, (480, 360)),  # 4:3, size decrease
        ((450, 800), 360, (360, 640)),  # 9:16, size decrease
        ((800, 450), 360, (640, 360)),  # 16:9, size decrease
        # Odd heights or widths should get adjusted downwards (125->124)
        ((120, 250), 60, (60, 124)),
        ((250, 120), 60, (124, 60)),
    ],
)
def test_resize_video_clip__success(original_size, short_edge_length_px, expected_size):
    with _generate_test_video(original_size) as video:
        resized_video = resize_video_clip(video, short_edge_length_px)
        assert resized_video.size == expected_size, (
            f"Expected video of size {expected_size} but was {resized_video.size}"
        )


@pytest.mark.unit
@pytest.mark.parametrize("size", [(360, 360), (360, 640), (640, 360)])
def test_resize_video_clip__no_resize(size):
    with _generate_test_video(size) as video:
        # Request the video to be resized to it's current size.
        resized_video = resize_video_clip(video, short_edge_length_px=min(size))

        # Check that no new VideoClip instance was created.
        assert resized_video is video, (
            f"Expected resized_video to reference {video} but was: {resized_video}"
        )


def _generate_test_video(size: Tuple[int, int], duration_sec: float = 5.0) -> VideoClip:
    """
    Create a black video of the specified size and duration.

    Args:
      - size (width, height): The dimensions of the video to generate.
      - duration_sec: The duration of the video to generate.
    """
    # ImageClip reads a (height x width x rbg) tensor whereas the ordering in the size
    # parameter is reversed (width, height). We use (width, height) as that's more
    # consistent with how moviepy normally orders the two values.
    width, height = size
    return ImageClip(np.full([height, width, 3], 0.0), duration=duration_sec)
