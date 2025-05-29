import os

import cairosvg
import cv2
from loguru import logger
from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip

from vikit.common.file_tools import get_canonical_name
from vikit.common.video_tools import write_videofile
from vikit.postprocessing.logo.model import LogoConfig

MINIMUM_RESOLUTION_THRESHOLD = 720


class VideoLogoOverlayer:
    def __init__(
        self,
        logo_config: LogoConfig,
    ):
        self.video_path = logo_config.input_video_path
        self.logo_path = logo_config.logo
        self.output_path = logo_config.output_video_name
        self.position = logo_config.position
        self.logo_height = logo_config.height_size_px
        self.logo_height_percentage = logo_config.logo_height_percentage
        self.margin = logo_config.margin_pix
        self.opacity = logo_config.opacity

    async def overlay_logo(self):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        if not os.path.exists(self.logo_path):
            raise FileNotFoundError(f"Logo file not found: {self.logo_path}")

        positions = {
            "top_right": ("right", "top"),
            "top_left": ("left", "top"),
            "bottom_right": ("right", "bottom"),
            "bottom_left": ("left", "bottom"),
        }

        video = VideoFileClip(self.video_path, fps_source="fps")

        if not self.logo_height:
            logger.debug(
                "No logo height provided. Automatically computing it based on the "
                "video height ..."
            )

            self.logo_height = int(video.h * (self.logo_height_percentage / 100))

        logger.debug(
            f"Started adding logo {self.logo_path} to video {self.video_path} ..."
        )

        # SVGs do not work with moviepy we need to transform them into PNGs in the
        # current working directory. We cannot transform them directly into WEBP so we
        # do it in two conversion steps.
        if self.logo_path.lower().endswith(".svg"):
            png_logo_path = get_canonical_name(self.logo_path) + ".png"
            cairosvg.svg2png(url=self.logo_path, write_to=png_logo_path)
            self.logo_path = os.path.abspath(png_logo_path)

        if self.logo_path.lower().endswith(".png"):
            webp_logo_path = get_canonical_name(self.logo_path) + ".webp"
            image = cv2.imread(self.logo_path, cv2.IMREAD_UNCHANGED)
            cv2.imwrite(webp_logo_path, image, [int(cv2.IMWRITE_WEBP_QUALITY), 100])
            self.logo_path = os.path.abspath(webp_logo_path)

        logo = ImageClip(self.logo_path)
        logo = logo.resize(height=int(self.logo_height))
        logo = logo.set_opacity(self.opacity)

        margins = {
            "top_right": {"right": self.margin, "top": self.margin},
            "top_left": {"left": self.margin, "top": self.margin},
            "bottom_right": {"right": self.margin, "bottom": self.margin},
            "bottom_left": {"left": self.margin, "bottom": self.margin},
        }

        logo = logo.set_position(positions[self.position], relative=True).margin(
            **margins[self.position],
            # This is the background opacity, not the logo opacity
            opacity=0,
        )
        logo = logo.set_duration(video.duration)

        final_video = CompositeVideoClip([video, logo])
        write_videofile(final_video, self.output_path, fps=video.fps)
