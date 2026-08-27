import json
from pathlib import Path

from retro_opt.games.dq6.story_events import default_data_dir, load_story_events


def _model_dir() -> Path:
    return default_data_dir().parent / "model"


def test_story_phases_cover_every_chart_event_exactly_once() -> None:
    payload = json.loads(
        (_model_dir() / "story_phases.json").read_text(encoding="utf-8")
    )

    covered: list[int] = []
    for phase in payload["phases"]:
        start, end = phase["chart_event_range"]
        covered.extend(range(start, end + 1))

    assert covered == list(range(1, 226))


def test_semantic_gate_event_references_exist() -> None:
    events = load_story_events()
    payload = json.loads(
        (_model_dir() / "story_progression_gates.json").read_text(encoding="utf-8")
    )

    gate_ids: set[str] = set()
    for gate in payload["gates"]:
        gate_id = gate["id"]
        assert gate_id not in gate_ids
        gate_ids.add(gate_id)

        for event_id in gate.get("after", []):
            assert event_id in events
        for event_id in gate.get("requires_chart_events", []):
            assert event_id in events


def test_known_hard_and_knowledge_bypassable_gates_are_distinguished() -> None:
    payload = json.loads(
        (_model_dir() / "story_progression_gates.json").read_text(encoding="utf-8")
    )
    gates = {gate["id"]: gate for gate in payload["gates"]}

    assert gates["river_passage_discovery_enabled"]["kind"] == "reachability_gate"
    assert gates["grace_hidden_stairs_revealed"]["kind"] == "knowledge_bypassable_gate"
    assert gates["ultimate_key_obtained"]["kind"] == "item_gate"
    assert gates["tenma_tower_entry_enabled"]["requires_item"] == "ultimate_key"
