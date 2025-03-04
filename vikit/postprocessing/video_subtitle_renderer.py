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
Subtitle Renderer class to add subtitles to a video
"""
from pathlib import Path

import pysrt
from loguru import logger
from moviepy.editor import ColorClip, CompositeVideoClip, TextClip, VideoFileClip
from PIL import ImageFont

FONT_SIZE_RATIO = 0.045


class VideoSubtitleRenderer:
    """
    A class to implement adding subtitle to a video
    - font_size in point (1 px = 0.75 pt; 1 pt = 1.333333 px), if none, it will be calculated based on the video height

    """

    def __init__(
        self,
        font_path=f"{Path(__file__).parent.parent.parent}/medias/arial.ttf",
        font_size_pt=None,
        margin_bottom_ratio=0.04,
        margin_right_ratio=0.05,
        margin_left_ratio=0.05,
    ) -> None:
        self.font_path = font_path
        self.font_size_pt = font_size_pt
        self.margin_bottom_ratio = margin_bottom_ratio
        self.margin_right_ratio = margin_right_ratio
        self.margin_left_ratio = margin_left_ratio
        self.codec = "libx264"

        self.min_resolution_threshold = 720

    def wrap_text(self, text, max_width, font_path, font_size_pt):
        """
        Wraps text into multiple lines based on the maximum width.

        Args:
            text (str): The original text.
            max_width (int): The maximum width for each line.
            font_path (str): Path to the font file.
            font_size_pt (int): Font size for the text in pt.

        Returns:
            str: Wrapped text with line breaks.
        """

        # Load the font to measure text dimensions
        font = ImageFont.truetype(font_path, font_size_pt)
        lines = []
        current_line = ""

        for word in text.split():
            test_line = f"{current_line} {word}".strip()
            # Use getbbox to calculate text width
            _, _, test_width, _ = font.getbbox(test_line)

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        # Add the last line
        lines.append(current_line)

        return "\n".join(lines)

    def add_subtitles_to_video(
        self,
        input_video_path: str,
        subtitle_srt_filepath: str,
        output_video_path: str,
        text_color: str = "white",
        highlight_color: tuple = (0, 0, 0),
        highlight_opacity: float = 1,
    ) -> None:
        """
        Append subtitle to a video and save it

        Args:
            input_video_path (str): The path to the video file
            subtitle_srt_filepath (str): The path to the subtitle srt file
            output_video_path (str): The path to save the output video
            highlight_color (tuple): The RGB value of the highlight text color
            highlight_opacity (float): The opacity/transparency level of the subtitle highlight

        Returns:
            bool: True if the video has an audio track, False otherwise

        """
        # Load the video
        logger.debug(f"Loading video from {input_video_path} to add subtitle ...")
        video = VideoFileClip(input_video_path)

        # Calculate the parameters relative to the video height
        font_size = self.font_size_pt or int(video.h * FONT_SIZE_RATIO)

        margin_bottom = int(video.h * self.margin_bottom_ratio)
        margin_left = int(video.w * self.margin_left_ratio)
        margin_right = int(video.w * self.margin_right_ratio)
        subs = pysrt.open(subtitle_srt_filepath)
        subtitle_clips = []

        # Iterate through the subtitles
        for sub in subs:
            start_time = (
                sub.start.hours * 3600
                + sub.start.minutes * 60
                + sub.start.seconds
                + sub.start.milliseconds / 1000.0
            )
            end_time = (
                sub.end.hours * 3600
                + sub.end.minutes * 60
                + sub.end.seconds
                + sub.end.milliseconds / 1000.0
            )

            # Sometimes srt file is longer than the real video, here is to avoid having black extra frames at the end
            start_time = max(0, start_time)
            end_time = min(video.duration, end_time)

            # Calculate the available width for the text
            available_width = video.w - margin_left - margin_right
            wrapped_text = self.wrap_text(
                sub.text, available_width, self.font_path, font_size
            )

            text_clip = TextClip(
                wrapped_text,
                fontsize=font_size,
                color=text_color,
                font=self.font_path,
                method="label",
                align="center",
            )

            # Get the exact dimensions of the rendered text
            text_width, text_height = text_clip.size

            # Calculate the position of the text clip with margins
            text_y_position = video.h - margin_bottom - text_height

            # Ensure the text does not overflow from the bottom
            if text_y_position < 0:
                text_y_position = 0

            # Set the position of the text clip with margins
            text_clip = (
                text_clip.set_position(("center", text_y_position))
                .set_fps(video.fps)
                .set_duration(end_time - start_time)
                .set_start(start_time)
            )

            bg_padding = 10

            # Highlight Clip
            bg_clip = (
                ColorClip(
                    size=(text_width + bg_padding * 2, text_height + bg_padding * 2),
                    color=highlight_color,
                    duration=end_time - start_time,
                )
                .set_fps(video.fps)
                .set_opacity(highlight_opacity)
                .set_start(start_time)
            )

            # Adjust background position to account for padding
            bg_position = (
                (video.w - (text_width + bg_padding * 2)) / 2,
                text_y_position - bg_padding,
            )
            bg_clip = (
                bg_clip.set_position(bg_position)
                .set_fps(video.fps)
                .set_start(start_time)
            )

            subtitle_clips.append(bg_clip)
            subtitle_clips.append(text_clip)
        # Overlay the text clips on the video
        final_video = (
            CompositeVideoClip([video] + subtitle_clips)
            .set_duration(video.duration)
            .set_start(video.start)
        )
        logger.debug(f"Saving video with subtitles to {output_video_path} ...")
        # Write the result to a file, keeping the original audio

        video_kwargs = {
            "codec": self.codec,
            "fps": video.fps,
            "audio_codec": "aac",
        }

        if max(final_video.size) < min_resolution_threshold:
            video_kwargs["bitrate"] = "14000k"

        final_video.write_videofile(output_video_path, **video_kwargs)
