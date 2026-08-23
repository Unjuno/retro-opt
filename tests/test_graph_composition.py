import pytest

from retro_opt.analysis.event_graph import validate_event_graph
from retro_opt.analysis.graph_composition import compose_event_graphs


def graph(graph_id: str, start: str, terminal: str, nodes: list[dict]):
    return {
        "schema_version": "0.1",
        "graph_id": graph_id,
        "start_node": start,
        "terminal_nodes": [terminal],
        "nodes": nodes,
    }


def test_compose_replaces_terminal_interface_with_downstream_start() -> None:
    upstream = graph(
        "up",
        "a",
        "b",
        [
            {"id": "a", "actions": [{"id": "go", "to": "b"}]},
            {"id": "b", "actions": []},
        ],
    )
    downstream = graph(
        "down",
        "b",
        "c",
        [
            {"id": "b", "actions": [{"id": "continue", "to": "c"}]},
            {"id": "c", "actions": []},
        ],
    )

    combined = compose_event_graphs(upstream, downstream)
    assert combined["start_node"] == "a"
    assert combined["terminal_nodes"] == ["c"]
    assert [node["id"] for node in combined["nodes"]] == ["a", "b", "c"]
    assert validate_event_graph(combined) == []


def test_downstream_start_must_match_upstream_terminal() -> None:
    upstream = graph(
        "up",
        "a",
        "b",
        [
            {"id": "a", "actions": [{"id": "go", "to": "b"}]},
            {"id": "b", "actions": []},
        ],
    )
    downstream = graph(
        "down",
        "x",
        "y",
        [
            {"id": "x", "actions": [{"id": "go", "to": "y"}]},
            {"id": "y", "actions": []},
        ],
    )

    with pytest.raises(ValueError, match="downstream start_node"):
        compose_event_graphs(upstream, downstream)
