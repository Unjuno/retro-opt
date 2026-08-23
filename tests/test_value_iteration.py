from __future__ import annotations

from dataclasses import dataclass

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.value_iteration import solve_ssp


@dataclass(frozen=True)
class ToyEnv:
    def actions(self, state: str) -> tuple[str, ...]:
        return {
            "start": ("direct", "detour"),
            "unprepared": ("finish",),
            "prepared": ("finish",),
            "goal": (),
        }[state]

    def transitions(self, state: str, action: str):
        table = {
            ("start", "direct"): (
                TransitionOutcome(1.0, "unprepared", 10.0),
            ),
            ("start", "detour"): (
                TransitionOutcome(1.0, "prepared", 20.0),
            ),
            ("unprepared", "finish"): (
                TransitionOutcome(0.5, "goal", 20.0),
                TransitionOutcome(0.5, "goal", 100.0),
            ),
            ("prepared", "finish"): (
                TransitionOutcome(1.0, "goal", 20.0),
            ),
        }
        return table[(state, action)]


def test_solver_prefers_globally_faster_detour() -> None:
    values, policy = solve_ssp(
        ToyEnv(),
        states=("start", "unprepared", "prepared", "goal"),
        terminal_states=("goal",),
    )

    # direct: 10 + (0.5*20 + 0.5*100) = 70 s
    # detour: 20 + 20 = 40 s
    assert policy["start"] == "detour"
    assert values["start"] == 40.0
