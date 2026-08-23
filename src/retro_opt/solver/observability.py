from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Hashable, TypeVar

from retro_opt.core.model import ObservationModel

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)
ObservationT = TypeVar("ObservationT", bound=Hashable)


def observation_conflicts(
    policy_by_state: Mapping[StateT, ActionT],
    observation_model: ObservationModel[StateT, ObservationT],
) -> dict[ObservationT, set[ActionT]]:
    """同じhuman observationに複数actionが割り当てられた箇所を返す。

    Competition policyはhidden stateを利用できないため、同一observationに属する
    statesでactionが一致しなければならない。
    """

    actions_by_observation: dict[ObservationT, set[ActionT]] = defaultdict(set)

    for state, action in policy_by_state.items():
        observation = observation_model.observe(state)
        actions_by_observation[observation].add(action)

    return {
        observation: actions
        for observation, actions in actions_by_observation.items()
        if len(actions) > 1
    }


def is_observation_consistent(
    policy_by_state: Mapping[StateT, ActionT],
    observation_model: ObservationModel[StateT, ObservationT],
) -> bool:
    """policyがhuman-observable informationだけで実行可能ならTrue。"""

    return not observation_conflicts(policy_by_state, observation_model)
