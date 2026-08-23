from __future__ import annotations

from math import inf, isclose
from typing import Collection, Hashable, Mapping, TypeVar

from retro_opt.core.model import StochasticEnvironment

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)


def solve_ssp(
    env: StochasticEnvironment[StateT, ActionT],
    states: Collection[StateT],
    terminal_states: Collection[StateT],
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100_000,
) -> tuple[dict[StateT, float], dict[StateT, ActionT]]:
    """期待所要時間を最小化する有限状態SSPをvalue iterationで解く。

    前提:
    - duration_seconds >= 0
    - terminal stateのvalueは0
    - 各(state, action)の遷移確率和は1
    - 少なくとも1つのproper policyが存在し、反復が収束する問題を対象とする

    戻り値:
    - 各stateの最小期待残時間 [s]
    - terminal以外のstateで選ぶgreedy action
    """

    terminal = set(terminal_states)
    values: dict[StateT, float] = {
        state: (0.0 if state in terminal else 0.0) for state in states
    }
    policy: dict[StateT, ActionT] = {}

    for _ in range(max_iterations):
        delta = 0.0
        next_values = values.copy()
        next_policy: dict[StateT, ActionT] = {}

        for state in states:
            if state in terminal:
                next_values[state] = 0.0
                continue

            actions = tuple(env.actions(state))
            if not actions:
                raise ValueError(f"non-terminal state has no legal actions: {state!r}")

            best_value = inf
            best_action: ActionT | None = None

            for action in actions:
                outcomes = tuple(env.transitions(state, action))
                if not outcomes:
                    raise ValueError(
                        f"action has no transition outcomes: state={state!r}, action={action!r}"
                    )

                probability_sum = sum(outcome.probability for outcome in outcomes)
                if not isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1e-12):
                    raise ValueError(
                        "transition probabilities must sum to 1: "
                        f"state={state!r}, action={action!r}, sum={probability_sum}"
                    )

                q_value = 0.0
                for outcome in outcomes:
                    if outcome.probability < 0.0:
                        raise ValueError("transition probability must be non-negative")
                    if outcome.duration_seconds < 0.0:
                        raise ValueError("duration_seconds must be non-negative")
                    if outcome.next_state not in values:
                        raise ValueError(
                            f"unknown next state: {outcome.next_state!r}"
                        )
                    q_value += outcome.probability * (
                        outcome.duration_seconds + values[outcome.next_state]
                    )

                if q_value < best_value:
                    best_value = q_value
                    best_action = action

            assert best_action is not None
            next_values[state] = best_value
            next_policy[state] = best_action
            delta = max(delta, abs(best_value - values[state]))

        values = next_values
        policy = next_policy
        if delta <= tolerance:
            return values, policy

    raise RuntimeError(
        f"value iteration did not converge within {max_iterations} iterations"
    )
