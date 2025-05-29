import os
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from vikit.common.global_constants import (
    ACCEPTED_IMAGE_FORMATS,
    ACCEPTED_VIDEO_FORMATS,
)


class LogoConfig(BaseModel):
    """
    The data model for the logo
    """

    input_video_path: str = Field(
        ...,
        description="Path to the video file to overlay the logo on. The path must be a public URL or a private accessible Google Cloud Storage URL.",
    )
    output_video_name: str = Field(
        ...,
        description="The output video name with the desired extension. Eg: vikit-pith.mp4.",
    )
    logo: str = Field(
        ...,
        description="The path to the logo file. The path must be a public URL or a private accessible Google Cloud Storage URL.",
    )
    position: Optional[
        Literal["top_left", "top_right", "bottom_left", "bottom_right"]
    ] = Field(
        "top_right",
        description="The position of the logo in the video, defaults to top_right (allowed values are top_left, top_right, bottom_left, bottom_right)",
    )
    margin_pix: Optional[int] = Field(
        20,
        description="The margin in pixels from the edges of the video (e.g., 10). Default value is 20",
        gt=0,
    )
    opacity: Optional[float] = Field(
        1.0,
        description="The opacity of the logo in the video (e.g., 0.5). Default value is 1.0 for opacity",
        ge=0.0,
        le=1.0,
    )
    height_size_px: Optional[float] = Field(
        None,
        description="The size in pixels of the logo in the video (e.g., 80).",
        gt=0,
    )
    logo_height_percentage: Optional[int] = Field(
        10,
        description="The height of the logo in percentage. This is used to compute the logo height in case the height_size_px is not provided. Default value is 10%",
        gt=0,
    )

    @field_validator("input_video_path", "output_video_name", mode="after")
    @classmethod
    def validate_video_path(cls, v, info):
        field_name = info.field_name
        if not v:
            raise ValueError(f"{field_name} must be set")

        file_extension = os.path.splitext(v)[1]
        if file_extension.lower() not in ACCEPTED_VIDEO_FORMATS:
            raise ValueError(
                f"{info.field_name} must have one of the following formats: {', '.join(ACCEPTED_VIDEO_FORMATS)}"
            )
        return v

    @field_validator("logo", mode="after")
    @classmethod
    def validate_logo_path(cls, v):
        if not v:
            raise ValueError("logo url must be set")

        file_extension = os.path.splitext(v)[1]
        if file_extension.lower() not in ACCEPTED_IMAGE_FORMATS:
            raise ValueError(
                f"logo must have one of the following formats: {', '.join(ACCEPTED_IMAGE_FORMATS)}"
            )
        return v
