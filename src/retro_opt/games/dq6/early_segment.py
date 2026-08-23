from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Sequence

from retro_opt.analysis.break_even import XpOutcome, validate_outcomes
from retro_opt.core.model import TransitionOutcome


@dataclass(frozen=True, slots=True)
class FarmingState:
    """序盤のEXP調整を抽象化した有限状態。"""

    exp: int
    opportunities_left: int
    terminal: bool = False


GOAL = FarmingState(exp=0, opportunities_left=0, terminal=True)


@dataclass(frozen=True, slots=True)
class ThresholdFarmingEnv:
    """追加戦闘の長期価値を検証するための仮説環境。

    downstream_penalty_seconds は「target_exp未達により後続で余計に必要になる時間」を
    抽象化した入力パラメータで、実ゲームの測定値ではない。
    """

    target_exp: int
    encounter_cost_seconds: float
    downstream_penalty_seconds: float
    xp_outcomes: tuple[XpOutcome, ...]

    def __post_init__(self) -> None:
        validate_outcomes(self.xp_outcomes)
        if self.target_exp < 0:
            raise ValueError("target_exp must be non-negative")
        if self.encounter_cost_seconds < 0.0:
            raise ValueError("encounter_cost_seconds must be non-negative")
        if self.downstream_penalty_seconds < 0.0:
            raise ValueError("downstream_penalty_seconds must be non-negative")

    def actions(self, state: FarmingState) -> Sequence[str]:
        if state.terminal:
            return ()
        if state.opportunities_left > 0:
            # 同値なら余計な戦闘をしない方を選ぶようskipを先に置く。
            return ("skip", "fight")
        return ("finish",)

    def transitions(
        self, state: FarmingState, action: str
    ) -> Sequence[TransitionOutcome[FarmingState]]:
        if state.terminal:
            raise ValueError("terminal state has no transitions")

        if state.opportunities_left > 0:
            next_left = state.opportunities_left - 1
            if action == "skip":
                return (
                    TransitionOutcome(
                        probability=1.0,
                        next_state=FarmingState(state.exp, next_left),
                        duration_seconds=0.0,
                    ),
                )
            if action == "fight":
                return tuple(
                    TransitionOutcome(
                        probability=outcome.probability,
                        next_state=FarmingState(
                            state.exp + outcome.xp_gain,
                            next_left,
                        ),
                        duration_seconds=self.encounter_cost_seconds,
                    )
                    for outcome in self.xp_outcomes
                )
            raise KeyError(action)

        if action != "finish":
            raise KeyError(action)
        penalty = 0.0 if state.exp >= self.target_exp else self.downstream_penalty_seconds
        return (
            TransitionOutcome(
                probability=1.0,
                next_state=GOAL,
                duration_seconds=penalty,
            ),
        )


def enumerate_reachable_states(
    env: ThresholdFarmingEnv,
    initial_states: Sequence[FarmingState],
) -> tuple[FarmingState, ...]:
    """有限horizonの仮説環境で到達可能状態を列挙する。"""

    seen = set(initial_states)
    seen.add(GOAL)
    queue = deque(initial_states)

    while queue:
        state = queue.popleft()
        if state.terminal:
            continue
        for action in env.actions(state):
            for outcome in env.transitions(state, action):
                next_state = outcome.next_state
                if next_state not in seen:
                    seen.add(next_state)
                    queue.append(next_state)

    return tuple(seen)
