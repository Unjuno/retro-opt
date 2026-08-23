from __future__ import annotations

from itertools import product
from math import inf, isclose
from typing import Collection, Hashable, Mapping, TypeVar

from retro_opt.core.model import StochasticEnvironment

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)


def evaluate_acyclic_policy(
    env: StochasticEnvironment[StateT, ActionT],
    *,
    initial_state: StateT,
    terminal_states: Collection[StateT],
    policy: Mapping[StateT, ActionT],
) -> float:
    """acyclic環境で固定policyの期待残時間 [s] を厳密再帰評価する。

    cycleを検出した場合はValueError。小規模solver検証用であり、大規模探索向けではない。
    """

    terminal = set(terminal_states)
    memo: dict[StateT, float] = {}
    visiting: set[StateT] = set()

    def visit(state: StateT) -> float:
        if state in terminal:
            return 0.0
        if state in memo:
            return memo[state]
        if state in visiting:
            raise ValueError("cycle detected in acyclic policy evaluator")
        if state not in policy:
            raise KeyError(f"policy has no action for state: {state!r}")

        visiting.add(state)
        action = policy[state]
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

        value = 0.0
        for outcome in outcomes:
            if outcome.probability < 0.0:
                raise ValueError("transition probability must be non-negative")
            if outcome.duration_seconds < 0.0:
                raise ValueError("duration_seconds must be non-negative")
            value += outcome.probability * (
                outcome.duration_seconds + visit(outcome.next_state)
            )

        visiting.remove(state)
        memo[state] = value
        return value

    return visit(initial_state)


def solve_bruteforce_acyclic(
    env: StochasticEnvironment[StateT, ActionT],
    *,
    states: Collection[StateT],
    terminal_states: Collection[StateT],
    initial_state: StateT,
) -> tuple[float, dict[StateT, ActionT]]:
    """全deterministic stationary policyを列挙するreference solver。

    decision state数に対して指数時間。小規模benchmarkで本solverの正しさを
    cross-checkするためだけに使用する。
    """

    terminal = set(terminal_states)
    decision_states: list[StateT] = []
    action_sets: list[tuple[ActionT, ...]] = []

    for state in states:
        if state in terminal:
            continue
        actions = tuple(env.actions(state))
        if not actions:
            raise ValueError(f"non-terminal state has no legal actions: {state!r}")
        decision_states.append(state)
        action_sets.append(actions)

    best_value = inf
    best_policy: dict[StateT, ActionT] | None = None

    for choices in product(*action_sets):
        policy = dict(zip(decision_states, choices, strict=True))
        value = evaluate_acyclic_policy(
            env,
            initial_state=initial_state,
            terminal_states=terminal,
            policy=policy,
        )
        if value < best_value:
            best_value = value
            best_policy = policy

    if best_policy is None:
        if initial_state in terminal:
            return 0.0, {}
        raise ValueError("no policy candidates were generated")

    return best_value, best_policy
