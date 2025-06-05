import os

import pytest

from tests.medias.references_for_tests import RANCHO_FONT, VIKIT_PITCH_MP4
from vikit.common.context_managers import WorkingFolderContext
from vikit.common.models import TimePeriod
from vikit.postprocessing.text_overlay.model import (
    TextOverlay,
    TextOverlayLine,
    TextOverlayLineStyle,
    TextOverlayPosition,
)
from vikit.postprocessing.text_overlay.renderer import render_text_overlay


@pytest.mark.local_integration
def test_render_text_overlay__valid_overlay():
    line_style1 = TextOverlayLineStyle(
        font_path=RANCHO_FONT,
        font_size_pt=30,
        text_color="#e2eeff",
        line_spacing_px=3,
        bg_color="#0b62b0",
        bg_padding_px=10,
        bg_corner_radius_px=10,
    )
    line_style2 = line_style1.model_copy(
        update={
            "font_weight": "bold",
            # Invert the colors
            "text_color": line_style1.bg_color,
            "bg_color": line_style1.text_color,
        },
    )
    line1 = TextOverlayLine(text="Clément Moutet")
    line2 = TextOverlayLine(
        text="Co-founder, CEO",
        line_style_override=line_style2,
    )
    line3 = TextOverlayLine(text="Vikit")
    text_overlay = TextOverlay(
        lines=[line1, line2, line3],
        line_style=line_style1,
        timing=TimePeriod(start_time_sec=0.0, end_time_sec=5.0),
        position=TextOverlayPosition(v_offset_px=300),
    )

    with WorkingFolderContext():
        dst_video_path = "video_with_overlay.mp4"
        render_text_overlay(
            src_video_path=VIKIT_PITCH_MP4,
            dst_video_path=dst_video_path,
            text_overlay=text_overlay,
        )
        assert os.path.exists(dst_video_path)
