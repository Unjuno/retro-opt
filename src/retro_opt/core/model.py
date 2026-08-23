from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Hashable, Protocol, Sequence, TypeVar

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)
ObservationT = TypeVar("ObservationT", bound=Hashable)


@dataclass(frozen=True, slots=True)
class TransitionOutcome(Generic[StateT]):
    """1つのactionから生じる確率的な遷移結果。"""

    probability: float
    next_state: StateT
    duration_seconds: float


class StochasticEnvironment(Protocol[StateT, ActionT]):
    """ゲーム固有実装からsolverを分離する最小interface。"""

    def actions(self, state: StateT) -> Sequence[ActionT]:
        """stateで合法なactionを返す。"""

    def transitions(
        self, state: StateT, action: ActionT
    ) -> Sequence[TransitionOutcome[StateT]]:
        """actionの遷移分布を返す。確率和は1でなければならない。"""


class ObservationModel(Protocol[StateT, ObservationT]):
    """完全状態を、人間が利用可能な観測へ写像するinterface。"""

    def observe(self, state: StateT) -> ObservationT:
        """hidden stateを含まないCompetition policy用の観測を返す。"""
