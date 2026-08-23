from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.break_even import (
    break_even_downstream_saving_seconds,
    metal_mixture_outcomes,
    threshold_cross_probability,
)

TARGET_EXP = 847
METAL_EXP = 1350
NORMAL_EXP_VALUES = (19, 19, 21, 23, 24)
CURRENT_EXP_VALUES = (800, 823, 824, 825, 826, 827, 828, 829, 830)
METAL_REWARD_PROBABILITIES = (0.01, 0.05, 0.10, 0.20)
NET_ENCOUNTER_COST_SECONDS = 10.0


def run() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for current_exp in CURRENT_EXP_VALUES:
        for metal_reward_probability in METAL_REWARD_PROBABILITIES:
            outcomes = metal_mixture_outcomes(
                metal_probability=metal_reward_probability,
                metal_xp=METAL_EXP,
                normal_xp_values=NORMAL_EXP_VALUES,
            )
            crossing_probability = threshold_cross_probability(
                current_xp=current_exp,
                target_xp=TARGET_EXP,
                outcomes=outcomes,
            )
            break_even = break_even_downstream_saving_seconds(
                net_encounter_cost_seconds=NET_ENCOUNTER_COST_SECONDS,
                crossing_probability=crossing_probability,
            )
            rows.append(
                {
                    "current_exp": current_exp,
                    "metal_reward_probability_assumption": metal_reward_probability,
                    "cross_probability": round(crossing_probability, 6),
                    "break_even_downstream_saving_seconds_at_10s_cost": (
                        None if break_even == float("inf") else round(break_even, 3)
                    ),
                }
            )

    return {
        "schema_version": "0.2",
        "experiment_id": "dq6-early-break-even-v0",
        "status": "sensitivity-only",
        "empirical_claim": False,
        "target_exp": TARGET_EXP,
        "metal_exp": METAL_EXP,
        "metal_probability_semantics": "effective probability that the encounter yields Metal Slime EXP; not appearance rate",
        "normal_exp_values": list(NORMAL_EXP_VALUES),
        "normal_outcome_assumption": (
            "conditional on non-metal-reward, listed values are treated as equally likely "
            "only for this sensitivity slice"
        ),
        "net_encounter_cost_seconds": NET_ENCOUNTER_COST_SECONDS,
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
