from __future__ import annotations

import json
from pathlib import Path

from retro_opt.analysis.event_graph import validate_event_graph
from retro_opt.analysis.graph_composition import compose_event_graphs


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
    errors = validate_event_graph(combined)

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-to-moon-mirror-composed-graph-sanity-v0",
        "component_paths": [str(path.relative_to(ROOT)) for path in PATHS],
        "node_count": len(combined["nodes"]),
        "terminal_count": len(combined["terminal_nodes"]),
        "start_node": combined["start_node"],
        "terminal_nodes": combined["terminal_nodes"],
        "error_count": len(errors),
        "pass": not errors,
        "errors": errors,
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
