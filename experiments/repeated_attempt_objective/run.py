from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.repeated_attempts import (
    expected_wall_clock_to_success_seconds,
)

POLICIES = (
    {
        "id": "aggressive",
        "success_probability": 0.10,
        "mean_success_duration_seconds": 380.0,
        "mean_failure_duration_seconds": 120.0,
    },
    {
        "id": "stable",
        "success_probability": 0.25,
        "mean_success_duration_seconds": 400.0,
        "mean_failure_duration_seconds": 180.0,
    },
    {
        "id": "tail-heavy",
        "success_probability": 0.05,
        "mean_success_duration_seconds": 360.0,
        "mean_failure_duration_seconds": 60.0,
    },
)


def run() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for policy in POLICIES:
        expected = expected_wall_clock_to_success_seconds(
            success_probability=policy["success_probability"],
            mean_success_duration_seconds=policy["mean_success_duration_seconds"],
            mean_failure_duration_seconds=policy["mean_failure_duration_seconds"],
        )
        rows.append({**policy, "expected_wall_clock_to_success_seconds": expected})

    rows.sort(key=lambda row: row["expected_wall_clock_to_success_seconds"])
    return {
        "schema_version": "0.1",
        "experiment_id": "repeated-attempt-objective-v0",
        "status": "synthetic-demo",
        "empirical_claim": False,
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
