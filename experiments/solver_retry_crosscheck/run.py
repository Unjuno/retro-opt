from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.value_iteration import solve_ssp

CASE_COUNT = 200
SEED = 20260824
TOLERANCE = 1e-8


@dataclass(frozen=True)
class RetryEnv:
    success_probability: float
    attempt_cost_seconds: float
    safe_cost_seconds: float

    def actions(self, state: str):
        if state == "goal":
            return ()
        return ("safe", "retry")

    def transitions(self, state: str, action: str):
        if action == "safe":
            return (TransitionOutcome(1.0, "goal", self.safe_cost_seconds),)
        if action == "retry":
            p = self.success_probability
            return (
                TransitionOutcome(p, "goal", self.attempt_cost_seconds),
                TransitionOutcome(1.0 - p, "start", self.attempt_cost_seconds),
            )
        raise KeyError(action)


def analytic_value(env: RetryEnv) -> float:
    # retryを永続的に選ぶstationary policyの期待時間は C/p。
    retry_value = env.attempt_cost_seconds / env.success_probability
    return min(env.safe_cost_seconds, retry_value)


def run() -> dict[str, object]:
    rng = random.Random(SEED)
    mismatches: list[dict[str, float | int]] = []
    max_absolute_error = 0.0

    for case_index in range(CASE_COUNT):
        env = RetryEnv(
            success_probability=rng.uniform(0.01, 0.99),
            attempt_cost_seconds=rng.uniform(0.1, 20.0),
            safe_cost_seconds=rng.uniform(1.0, 100.0),
        )
        expected = analytic_value(env)
        values, _ = solve_ssp(
            env,
            states=("start", "goal"),
            terminal_states=("goal",),
            tolerance=1e-12,
        )
        error = abs(values["start"] - expected)
        max_absolute_error = max(max_absolute_error, error)
        if error > TOLERANCE:
            mismatches.append(
                {
                    "case_index": case_index,
                    "analytic_value": expected,
                    "value_iteration_value": values["start"],
                    "absolute_error": error,
                }
            )

    return {
        "schema_version": "0.1",
        "experiment_id": "solver-retry-crosscheck-v0",
        "case_count": CASE_COUNT,
        "seed": SEED,
        "tolerance": TOLERANCE,
        "mismatch_count": len(mismatches),
        "max_absolute_error": max_absolute_error,
        "pass": not mismatches,
        "mismatches": mismatches,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
