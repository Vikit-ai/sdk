# ==============================================================================
#  Copyright 2025 Vikit.ai. All Rights Reserved.
# ==============================================================================

import ast
import os
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from vikit.common.global_constants import ACCEPTED_VIDEO_FORMATS


class SubtitleConfig(BaseModel):
    input_video_path: str = Field(
        ...,
        description="Path to the video file to overlay the subtitles on. The path must be a public URL or a private accessible Google Cloud Storage URL.",
    )
    output_video_name: str = Field(
        ...,
        description="The output video name with the desired extension. Eg: viki-pith.mp4.",
    )
    subtitle_srt_path: str = Field(
        ...,
        description="The path to the srt file that should follow the format: 1 \
                        00:00:00,000 --> 00:00:02,899 \
                        Mais par la cerise sur le gâteau la session de \
                        \
                        2 \
                        00:00:02,899 --> 00:00:05,799 \
                        rattrapage de Jean-Luc Lemoine et alors ce matin. Jean-luc nous recevons \
                        \
                        3 \
                        00:00:05,799 --> 00:00:08,699 \
                        donc Sarah Lecoeuvre active une bouchée pour parler de la rentrée médiatique. \
                        ",
    )
    text_color: Optional[str] = Field(
        "white",
        description="The color of the subtitle text (e.g., 'white', 'black', '#FFFFFF'). Default value is white",
    )
    highlight_color: Optional[str] = Field(
        "yellow",
        description="The color of the subtitle words highlighting (e.g., 'white', 'black', '#FFFFFF'). Default value is white",
    )
    bg_color: Optional[str] = Field(
        "(0,0,0)",
        description="The color of the subtitle text background highlight (e.g., 'white', 'black', '#FFFFFF'). Default value is (0,0,0)",
    )
    text_font: Optional[str] = Field(
        "Arial",
        description="The font family for the subtitle text (e.g., 'Arial', 'Times New Roman'). Arial is used by default.",
    )
    font_size_px: Optional[int] = Field(
        None,
        ge=0,
        description="The font size for the subtitle text in px (e.g., '14', '16').",
    )
    highlight_opacity: Optional[float] = Field(
        1,
        le=1,
        description="The opacity of the background highlight (e.g., '1', '0.9', '0.4').",
    )
    margin_bottom_ratio: Optional[float] = Field(
        0.04,
        description="The vertical margin ratio from the bottom of the video for subtitles. Default is 0.04.",
    )
    margin_left_ratio: Optional[float] = Field(
        0.05,
        description="The horizontal margin ratio from the left of the video for subtitles. Default is 0.05.",
    )
    margin_right_ratio: Optional[float] = Field(
        0.05,
        description="The horizontal margin ratio from the right of the video for subtitles. Default is 0.05.",
    )
    subtitle_style: Optional[str] = Field(
        "highlight_spoken_word",
        description=(
            "The subtitle display style. Available options:\n"
            "- `static_block`: Displays subtitles in blocks.\n"
            "- `highlight_spoken_word`: Highlights each word as it is spoken.\n"
            "- `highlight_spoken_sentence`: Highlights the entire sentence as it is spoken.\n"
            "- `place_words`: Displays words in real-time as they are spoken.\n"
            "Default: `highlight_spoken_word`."
        ),
    )

    @field_validator("subtitle_srt_path")
    @classmethod
    def validate_subtitle_srt_path(cls, v):
        if not v:
            raise ValueError("Subtitle SRT path must be set")

        if not v.endswith(".srt"):
            raise ValueError("Subtitle SRT path must have the .srt extension")

        return v

    @field_validator("input_video_path", "output_video_name", mode="before")
    @classmethod
    def validate_video_path(cls, v, info):
        field_name = info.field_name
        if not v:
            raise ValueError(f"{field_name.replace('_', ' ').capitalize()} must be set")

        file_extension = os.path.splitext(v)[1]
        if file_extension.lower() not in ACCEPTED_VIDEO_FORMATS:
            raise ValueError(
                f"{field_name.replace('_', ' ').capitalize()} must have one of the following formats: {', '.join(ACCEPTED_VIDEO_FORMATS)}"
            )
        return v

    @field_validator("font_size_px", mode="before")
    @classmethod
    def validate_font_size_px(cls, v):
        if v is None:
            raise ValueError("Font size px must be set")
        if v < 0:
            raise ValueError(
                f"Invalid font size px: {v}. It must be greater than or equal to 0."
            )
        return v

    @field_validator("font_size_px", "highlight_opacity", mode="before")
    @classmethod
    def validate_positive_number(cls, v, info):
        if v is None:
            if info.field_name == "font_size_px":
                return None  # Explicitly allow None
            raise ValueError(
                f"{info.field_name.replace('_', ' ').capitalize()} must be set"
            )

        if v < 0:
            raise ValueError(
                f"Invalid {info.field_name.replace('_', ' ')}: {v}. It must be greater than or equal to 0."
            )

        return v

    @field_validator("subtitle_style", mode="before")
    @classmethod
    def validate_subtitle_style(cls, v):
        valid_styles = [
            "static_block",
            "highlight_spoken_word",
            "highlight_spoken_sentence",
            "place_words",
        ]
        if v not in valid_styles:
            raise ValueError(
                f"Invalid subtitle style: {v}. Allowed values are {', '.join(valid_styles)}."
            )
        return v

    @field_validator("text_color", "highlight_color", "bg_color", mode="before")
    @classmethod
    def validate_color(cls, v, info):
        if isinstance(v, tuple):
            # Ensure tuple has 3 or 4 elements (RGB or RGBA)
            if len(v) == 3 and all(isinstance(i, int) and 0 <= i <= 255 for i in v):
                return f"rgb({v[0]},{v[1]},{v[2]})"  # Convert to "rgb(255,255,255)"
            if (
                len(v) == 4
                and all(isinstance(i, int) and 0 <= i <= 255 for i in v[:3])
                and isinstance(v[3], float)
                and 0 <= v[3] <= 1
            ):
                return f"rgba({v[0]},{v[1]},{v[2]},{v[3]})"  # Convert to "rgba(255,255,255,0.5)"
            raise ValueError(f"Invalid tuple color format: {v}")

        if isinstance(v, str):
            # Handle tuple-like strings, e.g., "(255, 255, 255)"
            if v.startswith("(") and v.endswith(")"):
                try:
                    parsed_tuple = ast.literal_eval(v)  # Convert to actual tuple
                    if isinstance(parsed_tuple, tuple):
                        return cls.validate_color(
                            parsed_tuple, info
                        )  # Revalidate as tuple with info
                except (SyntaxError, ValueError):
                    pass  # If conversion fails, fall back to regex validation

            # Regex for valid color formats
            pattern = (
                r"^#(?:[0-9a-fA-F]{3}){1,2}$"  # Hex: #FFF or #FFFFFF
                r"|^(white|black|red|green|blue|yellow|cyan|magenta|gray|grey)$"  # Named colors
                r"|^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$"  # RGB: rgb(255, 255, 255)
                r"|^rgba\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*(1|0?\.\d+)\s*\)$"  # RGBA: rgba(255, 255, 255, 0.5)
            )

            if re.match(pattern, v, re.IGNORECASE):
                return v

        raise ValueError(
            f"{info.field_name.replace('_', ' ').capitalize()} is given invalid color format: {v}"
        )
