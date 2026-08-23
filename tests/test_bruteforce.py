from __future__ import annotations

from dataclasses import dataclass

import pytest

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.bruteforce import solve_bruteforce_acyclic
from retro_opt.solver.value_iteration import solve_ssp


@dataclass(frozen=True)
class TinyDag:
    def actions(self, state: int) -> tuple[str, ...]:
        return {
            0: ("a", "b"),
            1: ("a", "b"),
            2: ("finish",),
            3: (),
        }[state]

    def transitions(self, state: int, action: str):
        table = {
            (0, "a"): (TransitionOutcome(1.0, 1, 5.0),),
            (0, "b"): (TransitionOutcome(1.0, 2, 8.0),),
            (1, "a"): (TransitionOutcome(1.0, 3, 10.0),),
            (1, "b"): (TransitionOutcome(1.0, 3, 20.0),),
            (2, "finish"): (TransitionOutcome(1.0, 3, 4.0),),
        }
        return table[(state, action)]


def test_exhaustive_reference_matches_value_iteration() -> None:
    env = TinyDag()
    states = (0, 1, 2, 3)
    brute_value, brute_policy = solve_bruteforce_acyclic(
        env,
        states=states,
        terminal_states=(3,),
        initial_state=0,
    )
    values, policy = solve_ssp(env, states=states, terminal_states=(3,))

    assert brute_value == pytest.approx(values[0])
    assert brute_value == 12.0
    assert brute_policy[0] == "b"
    assert policy[0] == "b"
