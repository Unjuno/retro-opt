from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.economy_boundaries import (
    minimum_starting_gold_for_spend,
    starting_gold_window_for_post_spend_balance,
)


IRON_SHIELD_PRICE = 720
IRON_SHIELD_COUNT = 2
TOTAL_SPEND = IRON_SHIELD_PRICE * IRON_SHIELD_COUNT
LOW_GOLD_RECOVERY_THRESHOLD = 140

SCENARIOS = (
    ("no_optional_inflow", ()),
    ("take_410g_chest", (410,)),
    ("legacy_sell_iron_claw_and_scale_shield", (525, 135)),
    ("legacy_sales_plus_410g", (410, 525, 135)),
    ("current_reference_sale_bundle", (697,)),
    ("current_bundle_plus_410g", (410, 697)),
)


def run() -> dict[str, object]:
    rows = []
    for scenario_id, inflows in SCENARIOS:
        rows.append(
            {
                "scenario_id": scenario_id,
                "known_inflows": list(inflows),
                "total_inflow_gold": sum(inflows),
                "minimum_starting_gold_for_two_shields": (
                    minimum_starting_gold_for_spend(
                        spend_gold=TOTAL_SPEND,
                        inflows=inflows,
                    )
                ),
                "starting_gold_window_where_two_shields_are_feasible_and_post_shop_gold_le_140": list(
                    starting_gold_window_for_post_spend_balance(
                        spend_gold=TOTAL_SPEND,
                        inflows=inflows,
                        max_post_spend_gold=LOW_GOLD_RECOVERY_THRESHOLD,
                    )
                    or ()
                ),
            }
        )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-post-horror-economy-boundaries-v0",
        "status": "structural-sensitivity-only",
        "empirical_claim": False,
        "iron_shield_price": IRON_SHIELD_PRICE,
        "iron_shield_count": IRON_SHIELD_COUNT,
        "total_spend_gold": TOTAL_SPEND,
        "low_gold_recovery_threshold": LOW_GOLD_RECOVERY_THRESHOLD,
        "assumptions": [
            "all listed inflows are realized before shield purchases",
            "transaction and detour time are excluded",
            "equipment combat value and future resale value are excluded",
            "the <=140G branch is a public-chart reference boundary, not a proven optimum"
        ],
        "sources": [
            "https://mamemommm.com/dq6_chart_mmm",
            "https://github.com/Maru0137/DQRTA-chart/blob/master/SFCDQ6RTA_stone_cut_chart.txt"
        ],
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
