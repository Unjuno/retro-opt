from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.event_graph import validate_event_graph


ROOT = Path(__file__).parents[2]
GRAPH = ROOT / "games" / "sfc" / "dq6" / "model" / "moon_mirror_resource_event_graph.json"


def run() -> dict[str, object]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    errors = validate_event_graph(graph)
    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-moon-mirror-graph-sanity-v0",
        "graph_path": str(GRAPH.relative_to(ROOT)),
        "node_count": len(graph["nodes"]),
        "terminal_count": len(graph["terminal_nodes"]),
        "error_count": len(errors),
        "pass": not errors,
        "errors": errors,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
