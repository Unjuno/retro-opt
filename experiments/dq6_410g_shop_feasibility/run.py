from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.purchase_feasibility import (
    starting_gold_window_where_pickup_unlocks,
)


PICKUP_GOLD = 410
IRON_SHIELD_PRICE = 720
TARGET_COUNTS = (1, 2)


def run() -> dict[str, object]:
    rows = []
    for target_count in TARGET_COUNTS:
        window = starting_gold_window_where_pickup_unlocks(
            pickup_gold=PICKUP_GOLD,
            unit_price=IRON_SHIELD_PRICE,
            target_units=target_count,
        )
        rows.append(
            {
                "target_iron_shield_count": target_count,
                "required_gold_without_pickup": IRON_SHIELD_PRICE * target_count,
                "starting_gold_window_where_410g_changes_feasibility": (
                    list(window) if window is not None else None
                ),
            }
        )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-410g-shop-feasibility-v0",
        "status": "structural-sensitivity-only",
        "empirical_claim": False,
        "pickup_gold": PICKUP_GOLD,
        "iron_shield_price": IRON_SHIELD_PRICE,
        "assumptions": [
            "sale income is excluded",
            "pickup/menu time is excluded",
            "future value after the shop is excluded",
            "this experiment tests purchase feasibility only, not route optimality"
        ],
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
