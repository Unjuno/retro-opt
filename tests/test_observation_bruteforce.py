from __future__ import annotations

from dataclasses import dataclass

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.observation_bruteforce import (
    solve_observation_policy_bruteforce_acyclic,
)


@dataclass(frozen=True)
class HiddenState:
    name: str
    hidden_rng: int
    terminal: bool = False


GOAL = HiddenState("goal", 0, terminal=True)


class Env:
    def actions(self, state: HiddenState):
        if state.terminal:
            return ()
        return ("left", "right")

    def transitions(self, state: HiddenState, action: str):
        if state.hidden_rng == 0:
            cost = 0.0 if action == "left" else 10.0
        else:
            cost = 10.0 if action == "left" else 0.0
        return (TransitionOutcome(1.0, GOAL, cost),)


class Observation:
    def observe(self, state: HiddenState) -> str:
        return state.name


def test_hidden_rng_cannot_be_used_by_observation_policy() -> None:
    state_a = HiddenState("same-screen", hidden_rng=0)
    state_b = HiddenState("same-screen", hidden_rng=1)

    value, policy = solve_observation_policy_bruteforce_acyclic(
        Env(),
        Observation(),
        states=(state_a, state_b, GOAL),
        terminal_states=(GOAL,),
        initial_distribution={state_a: 0.5, state_b: 0.5},
    )

    # hidden RNGが見えれば0秒を選び分けられるが、同一Observationでは同じactionを
    # 強制されるため期待値は5秒になる。
    assert value == 5.0
    assert policy["same-screen"] in {"left", "right"}
