"""
A class to overlay a logo on a video.
"""

import os

import cv2

from loguru import logger
from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip

MINIMUM_RESOLUTION_THRESHOLD = 720

class VideoLogoOverlay:
    """
    A class to overlay a logo on a video at a specified position.

    This class takes a video file and a logo image, resizes the logo,
    and overlays it onto the video at one of four predefined positions.
    """

    def __init__(
        self,
        video_path: str,
        logo_path: str,
        output_path: str,
        logo_height: int,
        position: str = "top_right",
        logo_height_percentage: int = 10,
        margin: int = 15,
    ):
        """
        Args:
            video_path (str): Path to the input video.
            logo_path (str): Path to the logo image.
            output_path (str): Path where the output video will be saved.
            position (str): Position to place the logo ('top_right', 'top_left', 'bottom_right', 'bottom_left').
            logo_height (int): The height of the logo in px.
            margin (int): The margins of the logo to each edge of the video in px. Default is 10.
        """
        self.video_path = video_path
        self.logo_path = logo_path
        self.output_path = output_path
        self.position = position
        self.logo_height = logo_height
        self.logo_height_percentage = logo_height_percentage
        self.margin = margin

        self.min_resolution_threshold = 720

    async def add_logo(self):
        """Adds the logo to the video and saves the output."""

        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        if not os.path.exists(self.logo_path):
            raise FileNotFoundError(f"Logo file not found: {self.logo_path}")
        if not self.output_path:
            raise ValueError("Output video path must be provided.")

        positions = {
            "top_right": ("right", "top"),
            "top_left": ("left", "top"),
            "bottom_right": ("right", "bottom"),
            "bottom_left": ("left", "bottom"),
        }

        if self.position not in positions:
            raise ValueError(
                "Invalid position value. Choose from 'top_right', 'top_left', 'bottom_right', 'bottom_left'."
            )

        video = VideoFileClip(self.video_path)

        if not self.logo_height:
            logger.debug(
                "No height provided. Automatically computing logo heigh based on video height ..."
            )

            self.logo_height = int(video.h * (self.logo_height_percentage / 100))

        logger.debug(
            f"Started adding logo {self.logo_path} to video {self.video_path} ..."
        )

        #There are issues with some PNGs transparency, converting to webp to be sure to avoid problems
        if self.logo_path.lower().endswith(".png"):
            try:
                webp_logo_path = self.logo_path.replace(".png", ".webp")
                image = cv2.imread(self.logo_path, cv2.IMREAD_UNCHANGED)
                cv2.imwrite(webp_logo_path, image, [int(cv2.IMWRITE_WEBP_QUALITY), 100])
                self.logo_path = webp_logo_path
            except Exception:
                raise RuntimeError("There was a problem with conversion from logo conversion from PNG to WEBP for smooth insertion into the video.")
        
        logo = ImageClip(self.logo_path)

        logo = logo.resize(height=int(self.logo_height))
        
        margins = {
            "top_right": {"right": self.margin, "top": self.margin},
            "top_left": {"left": self.margin, "top": self.margin},
            "bottom_right": {"right": self.margin, "bottom": self.margin},
            "bottom_left": {"left": self.margin, "bottom": self.margin},
        }

        logo = logo.set_position(positions[self.position], relative=True).margin(
            **margins[self.position], opacity=0
        )

        logo = logo.set_duration(video.duration)

        final_video = CompositeVideoClip([video, logo])

        video_kwargs = {
            "codec": "libx264",
            "fps": video.fps,
        }

        if max(final_video.size) < MINIMUM_RESOLUTION_THRESHOLD:
            video_kwargs["bitrate"] = "14000k"

        final_video.write_videofile(self.output_path, **video_kwargs)
