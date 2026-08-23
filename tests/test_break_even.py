from math import inf

import pytest

from retro_opt.analysis.break_even import (
    XpOutcome,
    break_even_downstream_saving_seconds,
    metal_mixture_outcomes,
    threshold_cross_probability,
)


def test_break_even_is_cost_divided_by_cross_probability() -> None:
    assert break_even_downstream_saving_seconds(
        net_encounter_cost_seconds=10.0,
        crossing_probability=0.25,
    ) == 40.0


def test_zero_cross_probability_is_never_worth_it_in_simple_model() -> None:
    assert break_even_downstream_saving_seconds(
        net_encounter_cost_seconds=10.0,
        crossing_probability=0.0,
    ) == inf


def test_threshold_cross_probability() -> None:
    outcomes = (
        XpOutcome(0.5, 10),
        XpOutcome(0.5, 30),
    )
    assert threshold_cross_probability(
        current_xp=820,
        target_xp=847,
        outcomes=outcomes,
    ) == 0.5


def test_dq6_reference_mixture_near_level7_threshold() -> None:
    # 非Metal時のEXP候補 19,19,21,23,24 を等確率とする仮説モデル。
    outcomes = metal_mixture_outcomes(
        metal_probability=0.05,
        metal_xp=1350,
        normal_xp_values=(19, 19, 21, 23, 24),
    )
    probability = threshold_cross_probability(
        current_xp=825,
        target_xp=847,
        outcomes=outcomes,
    )
    # 23,24 の2/5 + Metal 5% = 0.05 + 0.95*0.4 = 0.43
    assert probability == pytest.approx(0.43)
