from annotated_types import Ge
from pydantic import BaseModel, model_validator
from typing_extensions import Annotated


class TimePeriod(BaseModel):
    """A generic DTO to represent a time period, e.g in a video."""

    start_time_sec: Annotated[float, Ge(0.0), "seconds"]
    end_time_sec: Annotated[float, "seconds"]

    @model_validator(mode="after")
    def verify_end_time_sec(self):
        if not self.end_time_sec > self.start_time_sec:
            raise ValueError(
                f"End time ({self.end_time_sec}) must be greater than start time "
                f"({self.start_time_sec})"
            )
        return self
