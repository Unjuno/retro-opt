from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from retro_opt.analysis.parameter_audit import collect_unknown_references


GRAPH = (
    Path(__file__).parents[2]
    / "games"
    / "sfc"
    / "dq6"
    / "model"
    / "early_resource_event_graph.json"
)


def run() -> dict[str, object]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    references = collect_unknown_references(graph)
    counts = Counter(reference.value for reference in references)

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-resource-parameter-audit-v0",
        "graph_path": str(GRAPH.relative_to(Path(__file__).parents[2])),
        "unknown_reference_count": len(references),
        "unique_unknown_value_count": len(counts),
        "unknown_values": [
            {"value": value, "reference_count": counts[value]}
            for value in sorted(counts)
        ],
        "references": [
            {"path": reference.path, "value": reference.value}
            for reference in references
        ],
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
