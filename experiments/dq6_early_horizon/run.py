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
from retro_opt.solver.action_values import action_values
from retro_opt.solver.value_iteration import solve_ssp

TARGET_EXP = 847
METAL_PROBABILITY = 0.05
ENCOUNTER_COST_SECONDS = 10.0
DOWNSTREAM_PENALTY_SECONDS = 30.0
NORMAL_EXP_VALUES = (19, 19, 21, 23, 24)
METAL_EXP = 1350
SELECTED_EXP = (800, 805, 810, 823, 824, 825, 828)
HORIZONS = (1, 2, 3)


def run() -> dict[str, object]:
    env = ThresholdFarmingEnv(
        target_exp=TARGET_EXP,
        encounter_cost_seconds=ENCOUNTER_COST_SECONDS,
        downstream_penalty_seconds=DOWNSTREAM_PENALTY_SECONDS,
        xp_outcomes=metal_mixture_outcomes(
            metal_probability=METAL_PROBABILITY,
            metal_xp=METAL_EXP,
            normal_xp_values=NORMAL_EXP_VALUES,
        ),
    )

    starts = tuple(
        FarmingState(exp=exp, opportunities_left=horizon)
        for exp in SELECTED_EXP
        for horizon in HORIZONS
    )
    states = enumerate_reachable_states(env, starts)
    values, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))

    rows: list[dict[str, object]] = []
    for state in starts:
        q = action_values(env, state, values)
        rows.append(
            {
                "current_exp": state.exp,
                "opportunities_left": state.opportunities_left,
                "action": policy[state],
                "value_seconds": round(values[state], 3),
                "q_skip_seconds": round(q["skip"], 3),
                "q_fight_seconds": round(q["fight"], 3),
                "absolute_margin_seconds": round(abs(q["skip"] - q["fight"]), 3),
                "tie": abs(q["skip"] - q["fight"]) <= 1e-12,
            }
        )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-horizon-v0",
        "status": "sensitivity-only",
        "empirical_claim": False,
        "target_exp": TARGET_EXP,
        "metal_probability_assumption": METAL_PROBABILITY,
        "encounter_cost_seconds": ENCOUNTER_COST_SECONDS,
        "downstream_penalty_seconds": DOWNSTREAM_PENALTY_SECONDS,
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
