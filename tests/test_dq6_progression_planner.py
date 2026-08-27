from retro_opt.games.dq6.progression_planner import target_story_frontier
from retro_opt.games.dq6.state import DQ6State, PartyMemberState
from retro_opt.games.dq6.story_events import load_story_events


def _state() -> DQ6State:
    return DQ6State(
        segment="post_mermaid_harp",
        location="test",
        party=(PartyMemberState(name="hero", hp=100, mp=50, exp=5000, level=20),),
        completed_chart_events=frozenset(range(1, 143)),
    )


def test_intermediate_target_does_not_prune_other_legal_progression() -> None:
    events = load_story_events()
    state = _state()
    reachable = {event.place for event in events.values()}

    frontier = target_story_frontier(state, {179}, reachable, events)

    required_ready = {entry.event.chart_event_id for entry in frontier.required_ready}
    required_blocked = {entry.event.chart_event_id for entry in frontier.required_blocked}
    outside_ready = {
        entry.event.chart_event_id for entry in frontier.outside_target_ready
    }

    # Paths that feed the legendary-equipment merge at event 179.
    assert {144, 160, 170, 171, 178} <= required_ready

    # Best Dresser branch is structurally required, but its dedicated contest
    # capability model is not yet implemented, so it remains fail-closed.
    assert 159 in required_blocked

    # Ultimate Key is not an ancestor of event 179, but taking it now can still
    # matter later.  It must stay available to the global optimizer.
    assert 143 in outside_ready


def test_spatial_unreachability_blocks_without_changing_target_role() -> None:
    events = load_story_events()
    state = _state()

    frontier = target_story_frontier(state, {179}, {"lower_lifecod"}, events)

    required_ready = {entry.event.chart_event_id for entry in frontier.required_ready}
    required_blocked = {entry.event.chart_event_id for entry in frontier.required_blocked}

    assert 160 in required_ready
    assert 170 in required_blocked
    assert 171 in required_blocked

    blocked_170 = next(
        entry for entry in frontier.required_blocked if entry.event.chart_event_id == 170
    )
    assert blocked_170.spatial_status == "unreachable"
