from __future__ import annotations

from dataclasses import dataclass

from retro_opt.solver.observability import (
    is_observation_consistent,
    observation_conflicts,
)


@dataclass(frozen=True)
class State:
    visible_hp: int
    hidden_rng: int


class Observation:
    def observe(self, state: State) -> int:
        return state.visible_hp


def test_hidden_rng_cannot_change_competition_action() -> None:
    state_a = State(visible_hp=100, hidden_rng=1)
    state_b = State(visible_hp=100, hidden_rng=2)

    invalid_policy = {
        state_a: "attack",
        state_b: "defend",
    }

    conflicts = observation_conflicts(invalid_policy, Observation())

    assert conflicts == {100: {"attack", "defend"}}
    assert not is_observation_consistent(invalid_policy, Observation())


def test_visible_difference_may_change_action() -> None:
    policy = {
        State(visible_hp=100, hidden_rng=1): "attack",
        State(visible_hp=20, hidden_rng=2): "heal",
    }

    assert is_observation_consistent(policy, Observation())
