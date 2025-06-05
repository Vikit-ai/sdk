import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from vikit.common.models import TimePeriod


class TextOverlayLineStyle(BaseModel):
    font_path: str = Field(
        ..., description="The path of the font to use for the line text."
    )
    font_size_pt: int = Field(
        ...,
        description="The size of the font in point.",
        gt=0,
    )
    text_color: str = Field("white", description="The color of the font.")

    line_spacing_px: int = Field(
        0,
        description="The amount of space to leave between this line and the next.",
        ge=0,
    )

    bg_color: str = Field("black", description="The color of the background box.")
    bg_padding_px: int = Field(
        0,
        description="The amount of padding to add to the background box.",
        ge=0,
    )
    bg_corner_radius_px: float = Field(
        0.0,
        description="The corner radius to use for the background box. Set to 0 to "
        "disable round corners.",
        ge=0.0,
    )

    @field_validator("font_path")
    @classmethod
    def validate_font_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise FileNotFoundError(v)
        return v


class TextOverlayLine(BaseModel):
    text: str = Field(..., description="The text to display in this line.")
    line_style_override: Optional[TextOverlayLineStyle] = Field(
        None,
        description="Optional. The line style to apply to this line. If set, takes "
        "precedence over the global line style defined in TextOverlay.",
    )


class TextOverlayPosition(BaseModel):
    h_offset_px: int = Field(
        0,
        description="Horizontal offset of the text overlay from the center point.",
    )
    v_offset_px: int = Field(
        0,
        description="Vertical offset of the text overlay from the center point.",
    )


class TextOverlay(BaseModel):
    lines: List[TextOverlayLine] = Field(
        ...,
        description="The text lines to display.",
        min_length=1,
    )
    line_style: TextOverlayLineStyle = Field(
        ...,
        description="The global line style to apply to all lines which don't specify "
        "line_style_override.",
    )
    timing: TimePeriod = Field(
        ..., description="The time period during which to display the overlay."
    )
    position: Optional[TextOverlayPosition] = Field(
        None, description="Positioning parameters for the entire overlay."
    )
