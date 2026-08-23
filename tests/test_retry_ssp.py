from dataclasses import dataclass

import pytest

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.value_iteration import solve_ssp


@dataclass(frozen=True)
class RetryEnv:
    p: float
    retry_cost: float
    safe_cost: float

    def actions(self, state: str):
        return () if state == "goal" else ("safe", "retry")

    def transitions(self, state: str, action: str):
        if action == "safe":
            return (TransitionOutcome(1.0, "goal", self.safe_cost),)
        return (
            TransitionOutcome(self.p, "goal", self.retry_cost),
            TransitionOutcome(1.0 - self.p, "start", self.retry_cost),
        )


def test_retry_self_loop_matches_analytic_value() -> None:
    env = RetryEnv(p=0.2, retry_cost=1.0, safe_cost=10.0)
    values, policy = solve_ssp(
        env,
        states=("start", "goal"),
        terminal_states=("goal",),
    )

    assert values["start"] == pytest.approx(5.0)
    assert policy["start"] == "retry"
