from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.break_even import (
    break_even_downstream_saving_seconds,
    metal_encounter_outcomes,
    threshold_cross_probability,
)

TARGET_EXP = 847
METAL_APPEARANCE_PROBABILITY = 0.20
METAL_XP = 1350
NORMAL_EXP_VALUES = (19, 19, 21, 23, 24)
FAILED_METAL_XP = 0
KILL_PROBABILITIES = (0.25, 0.50, 0.75, 1.00)
CURRENT_EXP_VALUES = (800, 823, 824, 825, 826, 827, 828)
NET_ENCOUNTER_COST_SECONDS = 10.0


def run() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for current_exp in CURRENT_EXP_VALUES:
        for kill_probability in KILL_PROBABILITIES:
            outcomes = metal_encounter_outcomes(
                metal_appearance_probability=METAL_APPEARANCE_PROBABILITY,
                metal_kill_probability_given_appearance=kill_probability,
                metal_xp=METAL_XP,
                normal_xp_values=NORMAL_EXP_VALUES,
                failed_metal_xp=FAILED_METAL_XP,
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
                    "metal_kill_probability_given_appearance": kill_probability,
                    "effective_metal_reward_probability": round(
                        METAL_APPEARANCE_PROBABILITY * kill_probability, 6
                    ),
                    "cross_probability": round(crossing_probability, 6),
                    "break_even_downstream_saving_seconds": round(break_even, 3),
                }
            )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-metal-kill-sensitivity-v0",
        "status": "sensitivity-only",
        "empirical_claim": False,
        "target_exp": TARGET_EXP,
        "metal_appearance_probability_reference": METAL_APPEARANCE_PROBABILITY,
        "metal_appearance_probability_reference_quality": "approximate public RTA reference",
        "metal_xp": METAL_XP,
        "normal_exp_values": list(NORMAL_EXP_VALUES),
        "failed_metal_xp_assumption": FAILED_METAL_XP,
        "net_encounter_cost_seconds": NET_ENCOUNTER_COST_SECONDS,
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
