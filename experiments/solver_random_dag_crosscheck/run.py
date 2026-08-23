from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from retro_opt.core.model import TransitionOutcome
from retro_opt.solver.bruteforce import solve_bruteforce_acyclic
from retro_opt.solver.value_iteration import solve_ssp

CASE_COUNT = 200
STATE_COUNT = 6
SEED = 20260824
TOLERANCE = 1e-9


@dataclass(frozen=True)
class RandomDagEnv:
    table: dict[tuple[int, str], tuple[TransitionOutcome[int], ...]]

    def actions(self, state: int) -> tuple[str, ...]:
        if state == STATE_COUNT - 1:
            return ()
        return ("a", "b")

    def transitions(self, state: int, action: str):
        return self.table[(state, action)]


def _make_env(rng: random.Random) -> RandomDagEnv:
    table: dict[tuple[int, str], tuple[TransitionOutcome[int], ...]] = {}
    terminal = STATE_COUNT - 1

    for state in range(terminal):
        later = list(range(state + 1, STATE_COUNT))
        for action in ("a", "b"):
            duration = rng.uniform(0.1, 20.0)
            if len(later) == 1 or rng.random() < 0.5:
                next_state = rng.choice(later)
                outcomes = (TransitionOutcome(1.0, next_state, duration),)
            else:
                first, second = rng.sample(later, 2)
                probability = rng.uniform(0.05, 0.95)
                outcomes = (
                    TransitionOutcome(probability, first, duration),
                    TransitionOutcome(1.0 - probability, second, duration),
                )
            table[(state, action)] = outcomes

    return RandomDagEnv(table)


def run() -> dict[str, object]:
    rng = random.Random(SEED)
    states = tuple(range(STATE_COUNT))
    terminal = (STATE_COUNT - 1,)
    max_abs_error = 0.0
    mismatches: list[dict[str, float | int]] = []

    for case_index in range(CASE_COUNT):
        env = _make_env(rng)
        brute_value, _ = solve_bruteforce_acyclic(
            env,
            states=states,
            terminal_states=terminal,
            initial_state=0,
        )
        values, _ = solve_ssp(env, states=states, terminal_states=terminal)
        error = abs(brute_value - values[0])
        max_abs_error = max(max_abs_error, error)
        if error > TOLERANCE:
            mismatches.append(
                {
                    "case_index": case_index,
                    "bruteforce_value": brute_value,
                    "value_iteration_value": values[0],
                    "absolute_error": error,
                }
            )

    return {
        "schema_version": "0.1",
        "experiment_id": "solver-random-dag-crosscheck-v0",
        "case_count": CASE_COUNT,
        "state_count": STATE_COUNT,
        "seed": SEED,
        "tolerance": TOLERANCE,
        "mismatch_count": len(mismatches),
        "max_absolute_error": max_abs_error,
        "pass": not mismatches,
        "mismatches": mismatches,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
