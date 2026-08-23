from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from retro_opt.analysis.graph_composition import compose_event_graphs
from retro_opt.games.dq6.graph_codec_audit import audit_graph_codec


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
    issues = audit_graph_codec(combined)
    counts = Counter(issue.field for issue in issues)

    return {
        "schema_version": "0.1",
        "experiment_id": "dq6-early-to-moon-mirror-codec-audit-v0",
        "issue_count": len(issues),
        "issues_by_field": dict(sorted(counts.items())),
        "issues": [
            {
                "node_id": issue.node_id,
                "action_id": issue.action_id,
                "field": issue.field,
                "detail": issue.detail,
            }
            for issue in issues
        ],
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
