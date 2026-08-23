from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.break_even import metal_mixture_outcomes
from retro_opt.games.dq6.early_segment import (
    GOAL,
    FarmingState,
    ThresholdFarmingEnv,
    enumerate_reachable_states,
)
from retro_opt.solver.value_iteration import solve_ssp

TARGET_EXP = 847
METAL_PROBABILITY = 0.05
METAL_EXP = 1350
NORMAL_EXP_VALUES = (19, 19, 21, 23, 24)
ENCOUNTER_COST_SECONDS = 10.0
DOWNSTREAM_PENALTIES_SECONDS = (15.0, 30.0, 60.0)
CURRENT_EXP_VALUES = tuple(range(800, 831))


def solve_policy(downstream_penalty_seconds: float) -> dict[int, str]:
    env = ThresholdFarmingEnv(
        target_exp=TARGET_EXP,
        encounter_cost_seconds=ENCOUNTER_COST_SECONDS,
        downstream_penalty_seconds=downstream_penalty_seconds,
        xp_outcomes=metal_mixture_outcomes(
            metal_probability=METAL_PROBABILITY,
            metal_xp=METAL_EXP,
            normal_xp_values=NORMAL_EXP_VALUES,
        ),
    )
    starts = tuple(FarmingState(exp=xp, opportunities_left=1) for xp in CURRENT_EXP_VALUES)
    states = enumerate_reachable_states(env, starts)
    _, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))
    return {state.exp: policy[state] for state in starts}


def run() -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for penalty in DOWNSTREAM_PENALTIES_SECONDS:
        policy = solve_policy(penalty)
        fight_exp = [xp for xp, action in policy.items() if action == "fight"]
        cases.append(
            {
                "downstream_penalty_seconds": penalty,
                "first_exp_where_fight_is_optimal": min(fight_exp) if fight_exp else None,
                "policy": {str(xp): policy[xp] for xp in CURRENT_EXP_VALUES},
            }
        )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-policy-v0",
        "status": "sensitivity-only",
        "empirical_claim": False,
        "target_exp": TARGET_EXP,
        "metal_probability_assumption": METAL_PROBABILITY,
        "metal_exp": METAL_EXP,
        "normal_exp_values": list(NORMAL_EXP_VALUES),
        "normal_outcome_assumption": "equal weight conditional on non-metal",
        "encounter_cost_seconds": ENCOUNTER_COST_SECONDS,
        "cases": cases,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
