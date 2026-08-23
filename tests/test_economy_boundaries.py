import pytest

from retro_opt.analysis.economy_boundaries import (
    minimum_starting_gold_for_spend,
    post_spend_gold,
    starting_gold_window_for_post_spend_balance,
)


def test_minimum_starting_gold_accounts_for_inflows() -> None:
    assert minimum_starting_gold_for_spend(
        spend_gold=1440,
        inflows=(410, 660),
    ) == 370


def test_low_post_shop_balance_window() -> None:
    assert starting_gold_window_for_post_spend_balance(
        spend_gold=1440,
        inflows=(410, 660),
        max_post_spend_gold=140,
    ) == (370, 510)


def test_post_spend_gold() -> None:
    assert post_spend_gold(
        starting_gold=500,
        spend_gold=1440,
        inflows=(410, 660),
    ) == 130


def test_infeasible_spend_is_rejected() -> None:
    with pytest.raises(ValueError):
        post_spend_gold(
            starting_gold=100,
            spend_gold=1440,
            inflows=(410,),
        )
