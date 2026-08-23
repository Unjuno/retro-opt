from retro_opt.analysis.cumulative_thresholds import (
    pickup_reduces_threshold_debt,
    remaining_to_threshold,
    threshold_debt_vector,
)


def test_remaining_to_threshold() -> None:
    assert remaining_to_threshold(current=6, threshold=15) == 9
    assert remaining_to_threshold(current=15, threshold=15) == 0
    assert remaining_to_threshold(current=20, threshold=15) == 0


def test_threshold_debt_vector() -> None:
    assert threshold_debt_vector(current=6, thresholds=(15, 25, 15)) == (
        (15, 9),
        (25, 19),
    )


def test_one_medal_reduces_each_unreached_threshold_debt_by_one() -> None:
    assert pickup_reduces_threshold_debt(
        current=6,
        pickup_count=1,
        thresholds=(15, 25, 30, 40, 50, 60, 70),
    ) == (
        (15, 1),
        (25, 1),
        (30, 1),
        (40, 1),
        (50, 1),
        (60, 1),
        (70, 1),
    )


def test_reached_threshold_has_no_remaining_debt() -> None:
    assert pickup_reduces_threshold_debt(
        current=70,
        pickup_count=1,
        thresholds=(60, 70, 80),
    ) == (
        (60, 0),
        (70, 0),
        (80, 1),
    )
