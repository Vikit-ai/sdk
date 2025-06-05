import pytest
from pydantic import ValidationError

from vikit.common.models import TimePeriod


class TestTimePeriodValidation:
    @pytest.mark.unit
    def test_valid_entity(self):
        TimePeriod(start_time_sec=5.3, end_time_sec=12.0)

    @pytest.mark.unit
    def test_invalid_entity__start_time_sec_too_small(self):
        with pytest.raises(
            ValidationError, match="Input should be greater than or equal to 0"
        ):
            TimePeriod(start_time_sec=-1.0, end_time_sec=1.0)

    @pytest.mark.unit
    def test_invalid_entity__end_time_sec_too_small(self):
        with pytest.raises(
            ValidationError,
            match="End time \(1.0\) must be greater than start time \(2.0\)",
        ):
            TimePeriod(start_time_sec=2.0, end_time_sec=1.0)
