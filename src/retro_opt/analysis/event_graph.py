from __future__ import annotations

from collections import deque
from typing import Any, Mapping


def validate_event_graph(graph: Mapping[str, Any]) -> list[str]:
    """軽量なevent graph構造検証。外部schema libraryには依存しない。"""

    errors: list[str] = []
    raw_nodes = graph.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        return ["nodes must be a non-empty list"]

    node_ids: list[str] = []
    nodes_by_id: dict[str, Mapping[str, Any]] = {}
    for index, node in enumerate(raw_nodes):
        if not isinstance(node, Mapping):
            errors.append(f"nodes[{index}] must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(f"nodes[{index}].id must be a non-empty string")
            continue
        if node_id in nodes_by_id:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.append(node_id)
        nodes_by_id[node_id] = node

    start_node = graph.get("start_node")
    if start_node not in nodes_by_id:
        errors.append(f"unknown start_node: {start_node!r}")

    terminal_nodes = graph.get("terminal_nodes", [])
    if not isinstance(terminal_nodes, list) or not terminal_nodes:
        errors.append("terminal_nodes must be a non-empty list")
        terminal_nodes = []

    for terminal in terminal_nodes:
        if terminal not in nodes_by_id:
            errors.append(f"unknown terminal node: {terminal!r}")

    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for node_id, node in nodes_by_id.items():
        actions = node.get("actions", [])
        if actions is None:
            actions = []
        if not isinstance(actions, list):
            errors.append(f"node {node_id!r}: actions must be a list")
            continue

        if node_id in terminal_nodes and actions:
            errors.append(f"terminal node {node_id!r} must not have actions")

        for action_index, action in enumerate(actions):
            if not isinstance(action, Mapping):
                errors.append(
                    f"node {node_id!r}: action[{action_index}] must be an object"
                )
                continue
            action_id = action.get("id")
            if not isinstance(action_id, str) or not action_id:
                errors.append(
                    f"node {node_id!r}: action[{action_index}].id must be non-empty"
                )
            destination = action.get("to")
            if destination not in nodes_by_id:
                errors.append(
                    f"node {node_id!r} action {action_id!r}: unknown destination {destination!r}"
                )
            elif isinstance(destination, str):
                adjacency[node_id].add(destination)

    if isinstance(start_node, str) and start_node in adjacency:
        reachable: set[str] = set()
        queue = deque([start_node])
        while queue:
            node_id = queue.popleft()
            if node_id in reachable:
                continue
            reachable.add(node_id)
            queue.extend(adjacency[node_id] - reachable)

        unreachable = set(node_ids) - reachable
        for node_id in sorted(unreachable):
            errors.append(f"unreachable node from start: {node_id}")

        if terminal_nodes and not any(t in reachable for t in terminal_nodes):
            errors.append("no terminal node is reachable from start")

    return errors
