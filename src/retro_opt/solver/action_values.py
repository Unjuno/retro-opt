from __future__ import annotations

from math import isclose
from typing import Hashable, Mapping, TypeVar

from retro_opt.core.model import StochasticEnvironment

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)


def action_values(
    env: StochasticEnvironment[StateT, ActionT],
    state: StateT,
    values: Mapping[StateT, float],
) -> dict[ActionT, float]:
    """既知のvalue functionに対する各actionのQ値 [s] を返す。"""

    result: dict[ActionT, float] = {}
    for action in env.actions(state):
        outcomes = tuple(env.transitions(state, action))
        if not outcomes:
            raise ValueError(f"action has no outcomes: {action!r}")
        total_probability = sum(outcome.probability for outcome in outcomes)
        if not isclose(total_probability, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                f"transition probabilities must sum to 1, got {total_probability}"
            )

        q_value = 0.0
        for outcome in outcomes:
            if outcome.next_state not in values:
                raise KeyError(outcome.next_state)
            q_value += outcome.probability * (
                outcome.duration_seconds + values[outcome.next_state]
            )
        result[action] = q_value

    return result
