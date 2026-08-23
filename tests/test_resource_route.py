import pytest

from retro_opt.solver.value_iteration import solve_ssp
from retro_opt.synthetic.resource_route import (
    GOAL,
    START,
    ResourceDependencyEnv,
    ResourceRouteState,
    enumerate_reachable_states,
)


def test_solver_keeps_jointly_useful_detours() -> None:
    env = ResourceDependencyEnv()
    states = enumerate_reachable_states(env)
    values, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))

    # それぞれのpickupは局所的には時間増だが、組み合わせると
    # shieldを保持したままpotion購入が可能になりboss retry期待値を下げる。
    assert policy[START] == "take_shield"

    after_shield = ResourceRouteState("gold_chest", has_shield=True)
    assert policy[after_shield] == "take_gold"

    in_town = ResourceRouteState("town", has_shield=True, gold=50)
    assert policy[in_town] == "keep_shield"

    in_shop = ResourceRouteState("shop", has_shield=True, gold=50)
    assert policy[in_shop] == "buy_potion"

    assert values[START] == pytest.approx(63.60606060606061)


def test_single_resource_routes_are_worse_than_combination() -> None:
    env = ResourceDependencyEnv()
    states = enumerate_reachable_states(env)
    values, _ = solve_ssp(env, states=states, terminal_states=(GOAL,))

    shield_only_boss = ResourceRouteState("boss", has_shield=True)
    potion_only_boss = ResourceRouteState("boss", has_potion=True)
    both_boss = ResourceRouteState("boss", has_shield=True, has_potion=True)

    assert values[both_boss] < values[shield_only_boss]
    assert values[both_boss] < values[potion_only_boss]
