from __future__ import annotations

from collections import defaultdict
from itertools import product
from math import inf, isclose
from typing import Collection, Hashable, Mapping, TypeVar

from retro_opt.core.model import ObservationModel, StochasticEnvironment
from retro_opt.solver.bruteforce import evaluate_acyclic_policy

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)
ObservationT = TypeVar("ObservationT", bound=Hashable)


def solve_observation_policy_bruteforce_acyclic(
    env: StochasticEnvironment[StateT, ActionT],
    observation_model: ObservationModel[StateT, ObservationT],
    *,
    states: Collection[StateT],
    terminal_states: Collection[StateT],
    initial_distribution: Mapping[StateT, float],
) -> tuple[float, dict[ObservationT, ActionT]]:
    """human-observable policyを全列挙するacyclic reference solver。

    同じObservationに属するhidden statesでは同じactionを強制する。
    小規模benchmark専用で、observation数に対して指数時間。
    """

    terminal = set(terminal_states)
    probability_sum = sum(initial_distribution.values())
    if not isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(
            f"initial_distribution probabilities must sum to 1, got {probability_sum}"
        )
    if any(probability < 0.0 for probability in initial_distribution.values()):
        raise ValueError("initial distribution probability must be non-negative")

    states_by_observation: dict[ObservationT, list[StateT]] = defaultdict(list)
    for state in states:
        if state in terminal:
            continue
        states_by_observation[observation_model.observe(state)].append(state)

    observations: list[ObservationT] = []
    common_action_sets: list[tuple[ActionT, ...]] = []

    for observation, grouped_states in states_by_observation.items():
        first_actions = tuple(env.actions(grouped_states[0]))
        common_actions = [
            action
            for action in first_actions
            if all(action in env.actions(state) for state in grouped_states[1:])
        ]
        if not common_actions:
            raise ValueError(
                "states sharing an observation have no common legal action: "
                f"observation={observation!r}"
            )
        observations.append(observation)
        common_action_sets.append(tuple(common_actions))

    best_value = inf
    best_observation_policy: dict[ObservationT, ActionT] | None = None

    for choices in product(*common_action_sets):
        observation_policy = dict(zip(observations, choices, strict=True))
        state_policy = {
            state: observation_policy[observation_model.observe(state)]
            for state in states
            if state not in terminal
        }

        expected_value = 0.0
        for initial_state, probability in initial_distribution.items():
            expected_value += probability * evaluate_acyclic_policy(
                env,
                initial_state=initial_state,
                terminal_states=terminal,
                policy=state_policy,
            )

        if expected_value < best_value:
            best_value = expected_value
            best_observation_policy = observation_policy

    if best_observation_policy is None:
        if all(state in terminal for state in initial_distribution):
            return 0.0, {}
        raise ValueError("no observation-policy candidates were generated")

    return best_value, best_observation_policy
