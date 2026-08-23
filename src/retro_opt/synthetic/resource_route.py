from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from retro_opt.core.model import TransitionOutcome


@dataclass(frozen=True, slots=True)
class ResourceRouteState:
    stage: str
    has_shield: bool = False
    gold: int = 0
    has_potion: bool = False


GOAL = ResourceRouteState("goal")
START = ResourceRouteState("shield_chest")


class ResourceDependencyEnv:
    """item / gold / shop / boss riskの相互依存を検証するsynthetic環境。

    意図:
    - 近道だけ見ればoptional pickupは全て遅い。
    - shieldはそのままboss安定資源になる一方、売ってgoldにも変換できる。
    - gold chestは直接bossを強くしないが、shop purchaseを可能にする。
    - boss failureは同じpre-boss stateへ戻るretry loopとして表現する。

    数値はDQ6実測値ではない。solverが資源間の補完・代替関係を扱えるかを見る
    regression fixtureである。
    """

    def actions(self, state: ResourceRouteState) -> tuple[str, ...]:
        if state.stage == "shield_chest":
            return ("take_shield", "skip_shield")
        if state.stage == "gold_chest":
            return ("take_gold", "skip_gold")
        if state.stage == "town":
            if state.has_shield:
                return ("keep_shield", "sell_shield")
            return ("continue",)
        if state.stage == "shop":
            actions = ["skip_purchase"]
            if state.gold >= 50:
                actions.append("buy_potion")
            return tuple(actions)
        if state.stage == "boss":
            return ("attempt",)
        if state.stage == "goal":
            return ()
        raise KeyError(state.stage)

    def transitions(
        self, state: ResourceRouteState, action: str
    ) -> tuple[TransitionOutcome[ResourceRouteState], ...]:
        if state.stage == "shield_chest":
            if action == "take_shield":
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "gold_chest",
                            has_shield=True,
                            gold=state.gold,
                            has_potion=state.has_potion,
                        ),
                        8.0,
                    ),
                )
            if action == "skip_shield":
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "gold_chest",
                            has_shield=False,
                            gold=state.gold,
                            has_potion=state.has_potion,
                        ),
                        0.0,
                    ),
                )

        if state.stage == "gold_chest":
            if action == "take_gold":
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "town",
                            has_shield=state.has_shield,
                            gold=state.gold + 50,
                            has_potion=state.has_potion,
                        ),
                        12.0,
                    ),
                )
            if action == "skip_gold":
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "town",
                            has_shield=state.has_shield,
                            gold=state.gold,
                            has_potion=state.has_potion,
                        ),
                        0.0,
                    ),
                )

        if state.stage == "town":
            if action in {"keep_shield", "continue"}:
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "shop",
                            has_shield=state.has_shield,
                            gold=state.gold,
                            has_potion=state.has_potion,
                        ),
                        0.0,
                    ),
                )
            if action == "sell_shield" and state.has_shield:
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "shop",
                            has_shield=False,
                            gold=state.gold + 60,
                            has_potion=state.has_potion,
                        ),
                        3.0,
                    ),
                )

        if state.stage == "shop":
            if action == "skip_purchase":
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "boss",
                            has_shield=state.has_shield,
                            gold=state.gold,
                            has_potion=state.has_potion,
                        ),
                        0.0,
                    ),
                )
            if action == "buy_potion" and state.gold >= 50:
                return (
                    TransitionOutcome(
                        1.0,
                        ResourceRouteState(
                            "boss",
                            has_shield=state.has_shield,
                            gold=state.gold - 50,
                            has_potion=True,
                        ),
                        3.0,
                    ),
                )

        if state.stage == "boss" and action == "attempt":
            if state.has_shield and state.has_potion:
                clear_probability = 0.99
            elif state.has_shield:
                clear_probability = 0.65
            elif state.has_potion:
                clear_probability = 0.80
            else:
                clear_probability = 0.35

            return (
                TransitionOutcome(clear_probability, GOAL, 40.0),
                TransitionOutcome(1.0 - clear_probability, state, 60.0),
            )

        raise KeyError((state, action))


def enumerate_reachable_states(
    env: ResourceDependencyEnv,
    start: ResourceRouteState = START,
) -> tuple[ResourceRouteState, ...]:
    seen: set[ResourceRouteState] = {start}
    queue: deque[ResourceRouteState] = deque([start])

    while queue:
        state = queue.popleft()
        for action in env.actions(state):
            for outcome in env.transitions(state, action):
                if outcome.next_state not in seen:
                    seen.add(outcome.next_state)
                    queue.append(outcome.next_state)

    return tuple(seen)
