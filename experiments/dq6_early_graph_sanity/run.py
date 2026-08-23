from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.event_graph import validate_event_graph

ROOT = Path(__file__).resolve().parents[2]
GRAPH_PATH = ROOT / "games" / "sfc" / "dq6" / "model" / "early_event_graph.json"


def run() -> dict[str, object]:
    graph = json.loads(GRAPH_PATH.read_text())
    errors = validate_event_graph(graph)
    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-graph-sanity-v0",
        "graph_path": str(GRAPH_PATH.relative_to(ROOT)),
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
