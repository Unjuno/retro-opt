from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.cumulative_thresholds import (
    pickup_reduces_threshold_debt,
    threshold_debt_vector,
)


# Reference chart labels the Amor North Cave medal as the 7th medal,
# therefore the route-specific count immediately before pickup is 6.
CURRENT_MEDALS_BEFORE_PICKUP = 6
PICKUP_COUNT = 1
REWARD_THRESHOLDS = (15, 25, 30, 40, 50, 60, 70, 80, 90, 100)


def run() -> dict[str, object]:
    skip_debt = dict(
        threshold_debt_vector(
            current=CURRENT_MEDALS_BEFORE_PICKUP,
            thresholds=REWARD_THRESHOLDS,
        )
    )
    take_debt = dict(
        threshold_debt_vector(
            current=CURRENT_MEDALS_BEFORE_PICKUP + PICKUP_COUNT,
            thresholds=REWARD_THRESHOLDS,
        )
    )
    reduction = dict(
        pickup_reduces_threshold_debt(
            current=CURRENT_MEDALS_BEFORE_PICKUP,
            pickup_count=PICKUP_COUNT,
            thresholds=REWARD_THRESHOLDS,
        )
    )

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-medal-long-horizon-v0",
        "status": "structural-sensitivity-only",
        "empirical_claim": False,
        "route_specific_count_before_pickup": CURRENT_MEDALS_BEFORE_PICKUP,
        "pickup_count": PICKUP_COUNT,
        "source": "https://mamemommm.com/dq6_chart_mmm",
        "rows": [
            {
                "reward_threshold": threshold,
                "remaining_if_skip": skip_debt[threshold],
                "remaining_if_take": take_debt[threshold],
                "future_pickups_avoided_if_take": reduction[threshold],
            }
            for threshold in REWARD_THRESHOLDS
        ],
        "interpretation": (
            "This does not assign a time value to the medal. It records that the early "
            "pickup reduces later collection debt by one medal for every unreached "
            "cumulative reward threshold. The time value depends on which later medal "
            "pickup can be removed and on route timing."
        ),
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
