from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.event_graph import validate_event_graph
from retro_opt.analysis.graph_composition import compose_event_graphs


ROOT = Path(__file__).parents[2]
UPSTREAM = ROOT / "games" / "sfc" / "dq6" / "model" / "early_resource_event_graph.json"
DOWNSTREAM = ROOT / "games" / "sfc" / "dq6" / "model" / "post_amor_shop_economy_graph.json"


def run() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    downstream = json.loads(DOWNSTREAM.read_text(encoding="utf-8"))
    graph = compose_event_graphs(upstream, downstream)
    errors = validate_event_graph(graph)

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-composed-graph-sanity-v0",
        "components": graph["components"],
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
