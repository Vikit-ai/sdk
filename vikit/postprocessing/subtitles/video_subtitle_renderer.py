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
"""
This module provides functionality for rendering styled subtitles onto video clips.
It includes classes and utilities for processing subtitle data, splitting subtitles
into groups and lines, and rendering them with customizable styles and visual
properties.
"""

import os
import re
from dataclasses import dataclass
from typing import Generator, List, Literal, Optional, Tuple

from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    TextClip,
    VideoClip,
    VideoFileClip,
)
from PIL import ImageColor
from pysrt import SubRipFile

from vikit.common.subtitle_tools import trim_subtitles
from vikit.common.video_tools import write_videofile

# The maximum duration of each group of subtitles.
WORD_GROUP_DURATION_SEC = 3.0

# The amount of space to leave between the text and the left and right edges of the
# background box.
BG_PADDING_H_PX = 5

# The subtitle styles supported by the renderer.
SUBTITLE_STYLE = Literal[
    "static_block",
    "highlight_spoken_word",
    "highlight_spoken_sentence",
    "place_words",
]


class VideoSubtitleRenderer:
    """
    Renders styled subtitles onto video clips.

    Usage Example:
    ```python
    from vikit.postprocessing.subtitles.video_subtitle_renderer import \
        VideoSubtitleRenderer

    renderer = VideoSubtitleRenderer(
        subtitle_style="highlight_spoken_word",
        font_path="/path/to/font.ttf",
        font_size_pt=24,
        text_color="white",
        highlight_color="yellow",
        bg_color="black",
        bg_opacity=0.7,
        margin_bottom_px=50,
    )
    renderer.render(
        src_video_path="/path/to/input_video.mp4",
        dst_video_path="/path/to/output_video.mp4",
        subtitles_srt_path="/path/to/subtitles.srt",
    )
    ```
    """

    def __init__(
        self,
        subtitle_style: SUBTITLE_STYLE,
        font_path: str,
        font_size_pt: int,
        text_color: str,
        highlight_color: str,
        bg_color: str,
        bg_opacity: float,
        margin_bottom_px: int,
        margin_h_px: int,
    ) -> None:
        """
        Constructor for VideoSubtitleRenderer.

        This constructor sets up the renderer with the necessary configurations for
        rendering subtitles on a video and validates the provided parameters.

        Args:
            subtitle_style: The style of the subtitle. Supported options are:
                - "highlight_spoken_sentence": Highlights the entire sentence as it is
                  spoken.
                - "highlight_spoken_word": Highlights individual words as they are
                  spoken.
                - "place_words": Places words individually on the screen.
                - "static_block": Displays a static block of text without any
                  highlighting.
            font_path: The path to the font to use for the subtitle text.
            font_size_pt: The font size in points for the subtitle text.
            text_color: The color of the subtitle text. Can be a hex code, RGB/RGBA
                string, or a color name.
            highlight_color: The color used to highlight specific words or sentences in
                the subtitles. Can be a hex code, RGB/RGBA string, or a color name.
            bg_color: The background color for the subtitle box. Can be a hex code,
                RGB/RGBA string, or a color name.
            bg_opacity: The opacity of the background box, ranging from 0.0 (fully
                transparent) to 1.0 (fully opaque).
            margin_bottom_px: The margin in pixels between the bottom of the video frame
                and the bottom of the subtitles.
            margin_h_px: The margin in pixels between the horizontal edges of the video
                frame and the subtitles.

        Raises:
            FileNotFoundError: If the specified font file does not exist.
            ValueError: If any of the provided color values are invalid.
        """
        if subtitle_style not in SUBTITLE_STYLE.__args__:
            raise ValueError(
                f"subtitle_style ({subtitle_style}) must be one of "
                f"{SUBTITLE_STYLE.__args__}"
            )
        self._subtitle_style = subtitle_style

        if not os.path.exists(font_path):
            raise FileNotFoundError(font_path)
        self._font_path = font_path

        if not font_size_pt > 0:
            raise ValueError(f"font_size_pt ({font_size_pt}) must be > 0")
        self._font_size_pt = font_size_pt

        self._text_color = _normalize_color(text_color)
        self._highlight_color = _normalize_color(highlight_color)
        self._bg_color = _convert_color_to_rgb(bg_color)

        if not (0 <= bg_opacity <= 1):
            raise ValueError(f"bg_opacity ({bg_opacity}) must be in the range [0, 1]")
        self._bg_opacity = bg_opacity

        # Validated in the render method below.
        self._margin_bottom_px = margin_bottom_px
        self._margin_h_px = margin_h_px

    def render(
        self,
        src_video_path: str,
        dst_video_path: str,
        subtitles: SubRipFile,
    ) -> None:
        """
        Render a sub-section of the specified subtitles onto the given video, splitting
        the subtitles into readable chunks if necessary.

        Subtitles that are past the end of the video are ignored.

        The video with the rendered subtitles is saved to the specified output path.

        Args:
            src_video_path: The path to the input video file.
            dst_video_path: The path to the output video file.
            subtitles: The subtitles to render.
        """
        # Check parameters
        if not os.path.exists(src_video_path):
            raise FileNotFoundError(src_video_path)

        dst_video_dir = os.path.dirname(os.path.abspath(dst_video_path))
        if not os.path.exists(dst_video_dir):
            raise FileNotFoundError(dst_video_dir)

        with VideoFileClip(src_video_path, fps_source="fps") as input_video:
            if not 0 <= self._margin_bottom_px <= input_video.h:
                raise ValueError(
                    f"margin_bottom_px ({self._margin_bottom_px}) must be in the range "
                    f"[0, {input_video.h}]"
                )
            if not 0 <= self._margin_h_px <= int(input_video.w / 2):
                raise ValueError(
                    f"margin_h_px ({self._margin_h_px}) must be in the range "
                    f"[0, {int(input_video.w / 2)}]"
                )

            # Remove any subtitles that are past the end of the video.
            trimmed_subtitles = trim_subtitles(
                subtitles,
                start_time_sec=0.0,
                end_time_sec=input_video.duration,
            )
            if not trimmed_subtitles:
                raise ValueError(
                    f"No subtitles found in the specified time range: "
                    f"[{0}s, {input_video.duration}s]"
                )

            word_groups = _split_subtitles_by_group(
                trimmed_subtitles, group_duration_sec=WORD_GROUP_DURATION_SEC
            )
            subtitle_clips = []
            for word_group in word_groups:
                line_list = list(
                    _split_subtitles_by_line(
                        words=word_group,
                        max_width_px=input_video.w - 2 * self._margin_h_px,
                        font_path=self._font_path,
                        font_size_pt=self._font_size_pt,
                    )
                )
                group_clips = _render_subtitle_line_group(
                    group=_SubtitleLineGroup(line_list),
                    frame_size=input_video.size,
                    font_path=self._font_path,
                    font_size_pt=self._font_size_pt,
                    text_color=self._text_color,
                    highlight_color=self._highlight_color,
                    bg_color=self._bg_color,
                    bg_opacity=self._bg_opacity,
                    bg_padding_h_px=BG_PADDING_H_PX,
                    margin_bottom_px=self._margin_bottom_px,
                    subtitle_style=self._subtitle_style,
                )
                subtitle_clips.extend(group_clips)

            assert len(subtitle_clips) > 0
            final_video = CompositeVideoClip([input_video] + subtitle_clips)
            write_videofile(final_video, dst_video_path, fps=input_video.fps)


@dataclass
class _SubtitleWord:
    """A single subtitle word."""

    text: str

    start_sec: float
    end_sec: float

    width_px: Optional[int] = None
    height_px: Optional[int] = None

    @property
    def duration_sec(self) -> float:
        return self.end_sec - self.start_sec


@dataclass
class _SubtitleWordGroup:
    """An ordered collection of subtitle words, e.g. to represent a line."""

    # Assumed to be in chronological order based on their start times.
    words: List[_SubtitleWord]

    # Note: This width is not equal to the sum of widths of the words, because it also
    # includes the space between the words.
    width_px: Optional[int] = None

    @property
    def height_px(self) -> int:
        return max(word.height_px for word in self.words)

    @property
    def start_sec(self) -> float:
        return self.words[0].start_sec

    @property
    def end_sec(self) -> float:
        return self.words[-1].end_sec

    @property
    def duration_sec(self) -> float:
        return self.end_sec - self.start_sec

    def __iter__(self):
        return iter(self.words)

    def __len__(self):
        return len(self.words)


@dataclass
class _SubtitleLineGroup:
    """An ordered collection of subtitle lines to be displayed together."""

    # Assumed to be arranged from top to bottom.
    lines: List[_SubtitleWordGroup]

    @property
    def width_px(self) -> int:
        return max(line.width_px for line in self.lines)

    @property
    def height_px(self) -> int:
        return sum(line.height_px for line in self.lines)

    @property
    def start_sec(self) -> float:
        return self.lines[0].start_sec

    @property
    def end_sec(self) -> float:
        return self.lines[-1].end_sec

    @property
    def duration_sec(self) -> float:
        return self.end_sec - self.start_sec

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        return len(self.lines)


def _normalize_color(color: str | tuple) -> str:
    """
    Normalize a color string to a valid format.

    Args:
        color: The color to be normalized. This can either be a string (e.g., "#ff5733",
        "rgb(255, 0, 0)", a valid color name like "red", or a tuple representing RGB
        or RGBA values, e.g. (255, 0, 0) or (255, 0, 0, 1).

    Returns:
        A normalized string representing the color in a valid format, such as a hex
        color code, RGB, or RGBA.

    Raises:
        ValueError: If the input color format is invalid or unsupported.
    """
    if isinstance(color, tuple):
        if len(color) == 3 and all(0 <= c <= 255 for c in color):
            return f"rgb({color[0]}, {color[1]}, {color[2]})"
        if (
            len(color) == 4
            and all(0 <= c <= 255 for c in color[:3])
            and 0 <= color[3] <= 1
        ):
            return f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]})"

    if isinstance(color, str):
        color = color.strip()
        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
            return color
        if re.match(r"^rgb\((\d+),\s*(\d+),\s*(\d+)\)$", color):
            return color
        if color.lower() in ImageColor.colormap:
            return color.lower()

    raise ValueError(f"Invalid color format: {color}")


def _convert_color_to_rgb(color: str) -> tuple:
    """
    Convert a color string into an RGB or RGBA tuple.

    Args:
        color: The color to be converted. The string can be in various formats such as
        hex, RGB, or a known color name (e.g., "red").

    Returns:
        A tuple representing the color in RGB format, e.g., (255, 0, 0) for red.

    Raises:
        ValueError: If the input color format is invalid or unsupported.
    """
    if color.lower() == "transparent":
        return (0, 0, 0, 0)
    if color.startswith("#") or color.isalpha():
        return ImageColor.getrgb(color)
    if color.startswith("rgb"):
        color = color.strip("rgb()").replace(" ", "")
        return tuple(map(int, color.split(",")))
    raise ValueError(f"Invalid color format: {color}")


def _split_subtitles_by_group(
    subtitles: SubRipFile, group_duration_sec=3.0
) -> Generator[_SubtitleWordGroup, None, None]:
    """
    A generator that splits subtitles into groups based on the specified duration. The
    subtitles in a group are meant to be displayed together for the specified duration.

    Args:
        subtitles: The subtitles to split.
        group_duration_sec: The maximum duration of each subtitle group in seconds.

    Returns:
        A generator that yields each group in chronological order.
    """
    words = []
    duration = 0.0  # Running sum of the group duration, updated in the for loop.
    for item in subtitles:
        word = _SubtitleWord(
            item.text,
            item.start.ordinal / 1000.0,
            item.end.ordinal / 1000.0,
        )

        if duration + word.duration_sec > group_duration_sec:
            yield _SubtitleWordGroup(words)
            # Start a new group.
            words = []
            duration = 0.0

        words.append(word)
        duration += word.duration_sec

    if len(words) > 0:
        yield _SubtitleWordGroup(words)


def _split_subtitles_by_line(
    words: _SubtitleWordGroup,
    max_width_px: int,
    font_path: str,
    font_size_pt: int,
) -> Generator[_SubtitleWordGroup, None, None]:
    """
    A generator that splits a list of words into lines based on the frame size and font.

    Args:
        words: The list of words to split into lines.
        max_width_px: The maximum width of each line in pixels.
        font_path: The path to the font to use for the subtitle text.
        font_size_pt: The font size to use for the subtitle text in pt.

    Returns:
        A generator that yields each line of words in chronological order. The
        SubtitleWords in each line contain the measured dimensions.
    """
    space_width_px = TextClip(" ", font=font_path, fontsize=font_size_pt).w

    line_words = []
    line_width_px = 0  # running sum, updated in the for loop
    for word in words:
        # Update the word with the measured dimensions.
        word_clip = TextClip(word.text, font=font_path, fontsize=font_size_pt)
        word_with_dimension = _SubtitleWord(
            word.text, word.start_sec, word.end_sec, word_clip.w, word_clip.h
        )

        if line_width_px + word_clip.w > max_width_px:
            yield _SubtitleWordGroup(
                line_words,
                line_width_px - space_width_px,  # Don't count the last space.
            )
            # Start a new line.
            line_words = []
            line_width_px = 0

        line_words.append(word_with_dimension)
        line_width_px += word_with_dimension.width_px + space_width_px

    if len(line_words) > 0:
        yield _SubtitleWordGroup(
            line_words,
            line_width_px - space_width_px,  # Don't count the last space.
        )


def _render_subtitle_line_group(
    group: _SubtitleLineGroup,
    frame_size: Tuple[int, int],
    font_path: str,
    font_size_pt: int,
    text_color: str,
    highlight_color: str,
    bg_color: str,
    bg_opacity: float,
    bg_padding_h_px: int,
    margin_bottom_px: int,
    subtitle_style: SUBTITLE_STYLE,
) -> List[VideoClip]:
    """
    Create a series of text clips for the specified subtitle lines with the option to
    highlight words and apply custom subtitle styles, such as highlighting individual
    words or the entire spoken word.

    Generates word clips that are positioned on the video frame based on the specified
    styles and formatting options.

    The word clips are centered within the frame width based on the calculated
    line width.

    Args:
        group: The group of subtitle lines to be rendered.
        frame_size: A tuple containing the frame's width and height.
        font_path: The path to the font to use for the subtitle text.
        font_size_pt: The font size to use for the subtitle text in pt.
        text_color: The color of the subtitle text.
        highlight_color: The color for highlighting spoken words.
        bg_color: The color of the background box.
        bg_opacity: The opacity of the background box (0.0 to 1.0).
        bg_padding_h_px: The amount of space to leave between the text and the
            left and right edges of the background box.
        margin_bottom_px: The distance from the bottom of the frame to the
            bottom of the last line of text in pixels.
        subtitle_style: The style of the subtitle.

    Returns:
        A list of VideoClip objects that together render the subtitle group.
    """
    frame_width_px, frame_height_px = frame_size
    space_width_px = TextClip(" ", font=font_path, fontsize=font_size_pt).w

    # Calculate the vertical starting position of the text in this group.
    text_position_y = int(frame_height_px - margin_bottom_px - group.height_px)

    # Render the words and add the highlights and background boxes.
    bg_clips = []
    word_clips = []
    hl_clips = []

    # Render the background box for the whole group if required by the style.
    if bg_opacity > 0 and subtitle_style == "static_block":
        bg_position_x = frame_width_px / 2 - group.width_px / 2 - bg_padding_h_px
        bg_position_y = text_position_y
        bg_width_px = group.width_px + 2 * bg_padding_h_px
        bg_height_px = group.height_px
        bg_clip = (
            ColorClip(size=(bg_width_px, bg_height_px), color=bg_color)
            .set_position((bg_position_x, bg_position_y))
            .set_opacity(bg_opacity)
            .set_start(group.start_sec)
            .set_duration(group.duration_sec)
        )
        bg_clips.append(bg_clip)

    for line in group:
        # Calculate the vertical starting position of the text in this line.
        text_position_x = frame_width_px / 2 - line.width_px / 2

        # Render the background box for the line if required by the style.
        if bg_opacity > 0 and subtitle_style != "static_block":
            bg_position_x = text_position_x - bg_padding_h_px
            bg_position_y = text_position_y
            bg_width_px = line.width_px + 2 * bg_padding_h_px
            bg_height_px = line.height_px

            bg_clip = (
                ColorClip(size=(bg_width_px, bg_height_px), color=bg_color)
                .set_position((bg_position_x, bg_position_y))
                .set_opacity(bg_opacity)
                .set_start(group.start_sec)
                .set_duration(group.duration_sec)
            )
            bg_clips.append(bg_clip)

        for word in line:
            # Determine when to display the word and when to highlight it.
            if subtitle_style == "highlight_spoken_sentence":
                word_clip_start_sec = group.start_sec
                word_clip_duration_sec = group.duration_sec
                hl_clip_start_sec = word.start_sec
                hl_clip_duration_sec = (
                    group.start_sec + group.duration_sec - word.start_sec
                )
            elif subtitle_style == "highlight_spoken_word":
                word_clip_start_sec = group.start_sec
                word_clip_duration_sec = group.duration_sec
                hl_clip_start_sec = word.start_sec
                hl_clip_duration_sec = word.duration_sec
            elif subtitle_style == "place_words":
                word_clip_start_sec = word.start_sec
                word_clip_duration_sec = (
                    group.start_sec + group.duration_sec - word.start_sec
                )
                hl_clip_start_sec = word_clip_start_sec
                hl_clip_duration_sec = word_clip_duration_sec
            elif subtitle_style == "static_block":
                word_clip_start_sec = group.start_sec
                word_clip_duration_sec = group.duration_sec
                hl_clip_start_sec = None
                hl_clip_duration_sec = 0
            else:
                assert False, f"Unknown subtitle style: {subtitle_style}"

            word_clip = (
                TextClip(
                    word.text,
                    font=font_path,
                    fontsize=font_size_pt,
                    color=text_color,
                )
                .set_start(word_clip_start_sec)
                .set_duration(word_clip_duration_sec)
                .set_position((text_position_x, text_position_y))
            )
            word_clips.append(word_clip)
            if hl_clip_duration_sec > 0:
                hl_clip = (
                    TextClip(
                        word.text,
                        font=font_path,
                        fontsize=font_size_pt,
                        color=highlight_color,
                    )
                    .set_start(hl_clip_start_sec)
                    .set_duration(hl_clip_duration_sec)
                    .set_position((text_position_x, text_position_y))
                )
                hl_clips.append(hl_clip)

            text_position_x += word.width_px + space_width_px

        text_position_y += line.height_px

    return bg_clips + word_clips + hl_clips
