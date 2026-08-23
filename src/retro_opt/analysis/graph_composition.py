from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from retro_opt.analysis.event_graph import validate_event_graph


def compose_event_graphs(
    upstream: Mapping[str, Any],
    downstream: Mapping[str, Any],
) -> dict[str, Any]:
    """upstream terminal と downstream start を同名interfaceとして接合する。

    downstream start node の定義をinterface nodeとして採用する。したがって上流側では
    terminalだったnodeが、合成後には下流actionを持つ通常nodeになる。
    """

    upstream_errors = validate_event_graph(upstream)
    downstream_errors = validate_event_graph(downstream)
    if upstream_errors:
        raise ValueError(f"invalid upstream graph: {upstream_errors}")
    if downstream_errors:
        raise ValueError(f"invalid downstream graph: {downstream_errors}")

    interface = downstream["start_node"]
    upstream_terminals = tuple(upstream["terminal_nodes"])
    if interface not in upstream_terminals:
        raise ValueError(
            "downstream start_node must be one of upstream terminal_nodes: "
            f"{interface!r} not in {upstream_terminals!r}"
        )

    upstream_nodes = {node["id"]: deepcopy(node) for node in upstream["nodes"]}
    downstream_nodes = {node["id"]: deepcopy(node) for node in downstream["nodes"]}

    duplicate_ids = (set(upstream_nodes) & set(downstream_nodes)) - {interface}
    if duplicate_ids:
        raise ValueError(
            f"graphs contain duplicate non-interface node ids: {sorted(duplicate_ids)}"
        )

    upstream_nodes.pop(interface)
    merged_nodes = list(upstream_nodes.values()) + list(downstream_nodes.values())

    merged_terminals = [
        node_id for node_id in upstream_terminals if node_id != interface
    ]
    merged_terminals.extend(downstream["terminal_nodes"])

    result = {
        "schema_version": "0.1",
        "graph_id": f"{upstream.get('graph_id', 'upstream')}+{downstream.get('graph_id', 'downstream')}",
        "status": "composed",
        "start_node": upstream["start_node"],
        "terminal_nodes": list(dict.fromkeys(merged_terminals)),
        "nodes": merged_nodes,
        "components": [
            upstream.get("graph_id", "upstream"),
            downstream.get("graph_id", "downstream"),
        ],
    }

    errors = validate_event_graph(result)
    if errors:
        raise ValueError(f"composed graph is invalid: {errors}")
    return result
