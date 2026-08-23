from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from retro_opt.analysis.graph_composition import compose_event_graphs
from retro_opt.analysis.parameter_audit import collect_unknown_references


ROOT = Path(__file__).parents[2]
MODEL = ROOT / "games" / "sfc" / "dq6" / "model"
PATHS = (
    MODEL / "early_resource_event_graph.json",
    MODEL / "post_amor_shop_economy_graph.json",
    MODEL / "moon_mirror_resource_event_graph.json",
)


def run() -> dict[str, object]:
    graphs = [json.loads(path.read_text(encoding="utf-8")) for path in PATHS]
    combined = compose_event_graphs(graphs[0], graphs[1])
    combined = compose_event_graphs(combined, graphs[2])
    references = collect_unknown_references(combined)
    counts = Counter(reference.value for reference in references)

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-to-moon-mirror-parameter-audit-v0",
        "component_paths": [str(path.relative_to(ROOT)) for path in PATHS],
        "unknown_reference_count": len(references),
        "unique_unknown_value_count": len(counts),
        "unknown_values": [
            {"value": value, "reference_count": counts[value]}
            for value in sorted(counts)
        ],
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
