import pytest

from retro_opt.analysis.purchase_feasibility import (
    max_units_affordable,
    pickup_changes_affordability,
    starting_gold_window_where_pickup_unlocks,
)


def test_max_units_affordable() -> None:
    assert max_units_affordable(gold=1439, unit_price=720) == 1
    assert max_units_affordable(gold=1440, unit_price=720) == 2


def test_410g_pickup_can_unlock_one_720g_purchase() -> None:
    assert starting_gold_window_where_pickup_unlocks(
        pickup_gold=410,
        unit_price=720,
        target_units=1,
    ) == (310, 719)


def test_410g_pickup_can_unlock_two_720g_purchases() -> None:
    assert starting_gold_window_where_pickup_unlocks(
        pickup_gold=410,
        unit_price=720,
        target_units=2,
    ) == (1030, 1439)


def test_pickup_changes_affordability_at_boundary() -> None:
    assert pickup_changes_affordability(
        starting_gold=1030,
        pickup_gold=410,
        unit_price=720,
        target_units=2,
    )
    assert not pickup_changes_affordability(
        starting_gold=1029,
        pickup_gold=410,
        unit_price=720,
        target_units=2,
    )


def test_invalid_price_is_rejected() -> None:
    with pytest.raises(ValueError):
        max_units_affordable(gold=100, unit_price=0)
