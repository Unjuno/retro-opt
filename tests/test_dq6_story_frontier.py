from dataclasses import replace

import pytest

from retro_opt.games.dq6.state import DQ6State, PartyMemberState
from retro_opt.games.dq6.story_events import load_story_events
from retro_opt.games.dq6.story_frontier import (
    apply_story_event_completion,
    nonspatial_ready_story_events,
    ready_story_events,
    story_frontier,
)


def _hero(**kwargs: object) -> PartyMemberState:
    base = dict(name="hero", hp=100, mp=50, exp=5000, level=20)
    base.update(kwargs)
    return PartyMemberState(**base)


def _state(**kwargs: object) -> DQ6State:
    base = dict(segment="test", location="test", party=(_hero(),))
    base.update(kwargs)
    return DQ6State(**base)


def test_frontier_preserves_parallel_midgame_branches() -> None:
    events = load_story_events()
    state = _state(completed_chart_events=frozenset(range(1, 143)))

    ready_ids = {
        event.chart_event_id for event in nonspatial_ready_story_events(state, events)
    }

    # After Mermaid Harp (142), multiple independent progression branches are
    # simultaneously available.  A fixed chart order must not erase them.
    for event_id in (143, 144, 160, 170, 171, 178):
        assert event_id in ready_ids

    # Best Dresser rank 3 remains fail-closed until its dedicated capability
    # model can prove the contest requirements.
    assert 159 not in ready_ids


def test_spatial_filter_keeps_dependency_ready_distinct_from_reachable() -> None:
    events = load_story_events()
    state = _state(completed_chart_events=frozenset(range(1, 143)))

    entries = story_frontier(state, events)
    event_160 = next(entry for entry in entries if entry.event.chart_event_id == 160)
    assert event_160.nonspatial_ready
    assert event_160.spatial_status == "unchecked"
    assert not event_160.ready

    lifecod = {
        event.chart_event_id
        for event in ready_story_events(state, {"lower_lifecod"}, events)
    }
    assert 160 in lifecod
    assert 170 not in lifecod
    assert 171 not in lifecod

    seabed = {
        event.chart_event_id
        for event in ready_story_events(state, {"lower_seabed_temple"}, events)
    }
    assert 160 not in seabed
    assert 170 in seabed
    assert 171 in seabed


def test_resource_gate_survives_frontier_composition() -> None:
    events = load_story_events()
    state = _state(
        completed_chart_events=frozenset(range(1, 44)),
        gold=149,
    )

    entries = story_frontier(
        state,
        events,
        reachable_places={"lower_san_marino"},
    )
    ferry_ticket = next(entry for entry in entries if entry.event.chart_event_id == 44)
    assert ferry_ticket.spatial_status == "reachable"
    assert ferry_ticket.missing_non_spatial == ("gold>=150",)
    assert not ferry_ticket.ready

    ready = replace(state, gold=150)
    ready_ids = {
        event.chart_event_id
        for event in ready_story_events(ready, {"lower_san_marino"}, events)
    }
    assert 44 in ready_ids


def test_apply_completion_rejects_unmet_requirements_and_duplicates() -> None:
    events = load_story_events()
    event = events[44]
    state = _state(completed_chart_events=frozenset(range(1, 44)), gold=149)

    with pytest.raises(ValueError, match="gold>=150"):
        apply_story_event_completion(state, event)

    completed = apply_story_event_completion(replace(state, gold=150), event)
    assert 44 in completed.completed_chart_events

    with pytest.raises(ValueError, match="already completed"):
        apply_story_event_completion(completed, event)


def test_completion_does_not_invent_semantic_resource_effects() -> None:
    events = load_story_events()
    event = events[41]  # Dream Dew chest
    state = _state(completed_chart_events=frozenset(range(1, 41)))

    completed = apply_story_event_completion(state, event)
    assert 41 in completed.completed_chart_events
    assert completed.bag == ()
    assert "dream_dew_obtained" not in completed.story_flags
