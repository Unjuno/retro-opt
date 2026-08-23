import pytest

from retro_opt.analysis.repeated_attempts import (
    expected_wall_clock_to_success_seconds,
)


def test_expected_wall_clock_to_success() -> None:
    assert expected_wall_clock_to_success_seconds(
        success_probability=0.5,
        mean_success_duration_seconds=100.0,
        mean_failure_duration_seconds=50.0,
    ) == pytest.approx(150.0)


def test_certain_success_is_just_success_duration() -> None:
    assert expected_wall_clock_to_success_seconds(
        success_probability=1.0,
        mean_success_duration_seconds=100.0,
        mean_failure_duration_seconds=999.0,
    ) == pytest.approx(100.0)
