from retro_opt.analysis.event_graph import validate_event_graph


def test_valid_event_graph_has_no_errors() -> None:
    graph = {
        "start_node": "a",
        "terminal_nodes": ["c"],
        "nodes": [
            {"id": "a", "actions": [{"id": "go", "to": "b"}]},
            {"id": "b", "actions": [{"id": "finish", "to": "c"}]},
            {"id": "c", "actions": []},
        ],
    }
    assert validate_event_graph(graph) == []


def test_dangling_destination_is_reported() -> None:
    graph = {
        "start_node": "a",
        "terminal_nodes": ["c"],
        "nodes": [
            {"id": "a", "actions": [{"id": "go", "to": "missing"}]},
            {"id": "c", "actions": []},
        ],
    }
    errors = validate_event_graph(graph)
    assert any("unknown destination" in error for error in errors)
    assert any("unreachable node" in error for error in errors)
