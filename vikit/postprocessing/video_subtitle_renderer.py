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

import pysrt
from loguru import logger
from moviepy.editor import ColorClip, CompositeVideoClip, TextClip, VideoFileClip


class VideoSubtitleRenderer:
    """
    A class to implement adding subtitle to a video
    """

    def __init__(
        self,
        font_path="../../medias/arial.ttf",
        font_size_ratio=0.05,
        margin_bottom_ratio=0.03,
        margin_right_ratio=0.05,
        margin_left_ratio=0.05,
    ) -> None:
        self.font_path = font_path
        self.font_size_ratio = font_size_ratio
        self.margin_bottom_ratio = margin_bottom_ratio
        self.margin_right_ratio = margin_right_ratio
        self.margin_left_ratio = margin_left_ratio
        self.codec = "libx264"

    def add_subtitles_to_video(
        self,
        input_video_path: str,
        subtitle_srt_filepath: str,
        output_video_path: str,
        highlight_color: tuple = (0, 0, 0),
        highlight_opacity: float = 0.4,
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
        video_duration = video.duration  # Get the original video duration

        # Calculate the parameters relative to the video height
        font_size = int(video.h * self.font_size_ratio)
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
            if start_time < 0:
                start_time = 0
            if end_time > video_duration:
                end_time = video_duration

            # Text Clip
            # Calculate the available width for the text
            available_width = video.w - margin_left - margin_right

            text_clip = TextClip(
                sub.text,
                fontsize=font_size,
                color="white",
                font=self.font_path,
                method="caption",
                size=(available_width, None),
            )

            # Calculate the position of the text clip with margins
            text_height = text_clip.h
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

            # Highlight Clip
            bg_clip = (
                ColorClip(
                    size=(int(text_clip.w * 1.0), int(text_clip.h * 1.05)),
                    color=highlight_color,
                    duration=end_time - start_time,
                )
                .set_fps(video.fps)
                .set_opacity(highlight_opacity)
                .set_start(start_time)
            )

            # Calculate and set the position of the background clip
            bg_position = ((video.w - bg_clip.w) / 2, text_y_position)
            bg_clip = bg_clip.set_position(bg_position)

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
        final_video.write_videofile(
            output_video_path,
            fps=video.fps,
            codec=self.codec,
            audio_codec="aac",
        )
