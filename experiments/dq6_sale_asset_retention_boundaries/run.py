from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.economy_boundaries import minimum_starting_gold_for_spend


SPEND_GOLD = 1440
FIXED_410G_PICKUP = 410
IRON_CLAW_SALE = 525
SCALE_SHIELD_SALE = 135


def run() -> dict[str, object]:
    thresholds = {
        "sell_both": minimum_starting_gold_for_spend(
            spend_gold=SPEND_GOLD,
            inflows=(FIXED_410G_PICKUP, IRON_CLAW_SALE, SCALE_SHIELD_SALE),
        ),
        "sell_iron_claw_only": minimum_starting_gold_for_spend(
            spend_gold=SPEND_GOLD,
            inflows=(FIXED_410G_PICKUP, IRON_CLAW_SALE),
        ),
        "sell_scale_shield_only": minimum_starting_gold_for_spend(
            spend_gold=SPEND_GOLD,
            inflows=(FIXED_410G_PICKUP, SCALE_SHIELD_SALE),
        ),
        "sell_none": minimum_starting_gold_for_spend(
            spend_gold=SPEND_GOLD,
            inflows=(FIXED_410G_PICKUP,),
        ),
    }

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-sale-asset-retention-boundaries-v0",
        "status": "structural-sensitivity-only",
        "empirical_claim": False,
        "fixed_assumptions": {
            "take_410g_chest": True,
            "buy_two_iron_shields": True,
            "iron_shield_total_spend_gold": SPEND_GOLD,
            "iron_claw_sale_value_gold": IRON_CLAW_SALE,
            "scale_shield_sale_value_gold": SCALE_SHIELD_SALE
        },
        "minimum_starting_gold": thresholds,
        "starting_gold_regions": [
            {
                "min": thresholds["sell_both"],
                "max": thresholds["sell_iron_claw_only"] - 1,
                "structural_result": "both known assets must be sold to fund two shields"
            },
            {
                "min": thresholds["sell_iron_claw_only"],
                "max": thresholds["sell_scale_shield_only"] - 1,
                "structural_result": "selling iron_claw alone can fund the purchase; scale_shield alone cannot"
            },
            {
                "min": thresholds["sell_scale_shield_only"],
                "max": thresholds["sell_none"] - 1,
                "structural_result": "scale_shield alone can be sold, allowing iron_claw retention"
            },
            {
                "min": thresholds["sell_none"],
                "max": null,
                "structural_result": "no sale is required for the two-shield purchase"
            }
        ],
        "sources": [
            "https://mamemommm.com/dq6_chart_mmm",
            "https://github.com/Maru0137/DQRTA-chart/blob/master/SFCDQ6RTA_stone_cut_chart.txt"
        ],
        "interpretation": "This experiment does not decide whether iron_claw should be retained. It identifies the gold ranges where retention is economically feasible before adding combat value and transaction time."
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
