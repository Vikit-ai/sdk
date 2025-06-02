# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os

from moviepy.editor import VideoFileClip
from pysrt import SubRipFile

from medias import ARIAL_TTF_PATH
from vikit.postprocessing.subtitles.video_subtitle_renderer import (
    VideoSubtitleRenderer,
)

FONT_SIZE_RATIO = 0.045
PIXEL_TO_POINT = 0.75


class SimpleVideoSubtitleRenderer:
    """
    A subtitle renderer with sensible parameter defaults for simple use cases.

    Delegates the rendering to the VideoSubtitleRenderer class which can also be used
    directly if finer control is needed.
    """

    def __init__(
        self,
        font_path=ARIAL_TTF_PATH,
        font_size_pt=None,
        margin_bottom_ratio=0.04,
        margin_h_ratio=0.05,
    ) -> None:
        self.font_path = font_path
        self.font_size_pt = font_size_pt

        if not 0 <= margin_bottom_ratio <= 1:
            raise ValueError(
                f"margin_bottom_ratio ({margin_bottom_ratio}) must be in the range "
                "[0, 1]"
            )
        self.margin_bottom_ratio = margin_bottom_ratio

        if not 0 <= margin_h_ratio <= 1:
            raise ValueError(
                f"margin_h_ratio ({margin_h_ratio}) must be in the range [0, 1]"
            )
        self.margin_h_ratio = margin_h_ratio

    def add_subtitles_to_video(
        self,
        input_video_path: str,
        subtitle_srt_filepath: str,
        output_video_path: str,
        text_color: str = "white",
        highlight_color: str = "black",
        highlight_opacity: float = 0.7,
    ) -> None:
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(input_video_path)

        with VideoFileClip(input_video_path, fps_source="fps") as input_video:
            video_width_px, video_height_px = input_video.size

        if self.font_size_pt is not None:
            font_size_px = self.font_size_pt
        else:
            # Calculate font size in pixels based on video height
            font_size_px = int(video_height_px * FONT_SIZE_RATIO)

        if not os.path.exists(subtitle_srt_filepath):
            raise FileNotFoundError(subtitle_srt_filepath)

        try:
            subtitles = SubRipFile.open(
                subtitle_srt_filepath, error_handling=SubRipFile.ERROR_RAISE
            )
        except Exception as e:
            raise ValueError(
                f"Failed to parse subtitle file {subtitle_srt_filepath}: {e}"
            ) from e

        renderer = VideoSubtitleRenderer(
            subtitle_style="highlight_spoken_word",
            font_path=self.font_path,
            font_size_pt=font_size_px,
            text_color=text_color,
            highlight_color=highlight_color,
            bg_color="black",
            bg_opacity=highlight_opacity,
            margin_bottom_px=int(self.margin_bottom_ratio * video_height_px),
            margin_h_px=int(self.margin_h_ratio * video_width_px),
        )
        renderer.render(input_video_path, output_video_path, subtitles)
