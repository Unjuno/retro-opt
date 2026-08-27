from retro_opt.games.dq6.story_events import (
    ancestor_closure,
    legal_next_events,
    load_story_events,
    topological_order,
    validate_story_events,
)


def test_story_event_ids_cover_full_external_flag_chart() -> None:
    events = load_story_events()
    assert set(events) == set(range(1, 226))
    assert validate_story_events(events) == ()


def test_known_dependency_merges_are_preserved() -> None:
    events = load_story_events()

    assert events[14].requires == (12, 13)
    assert events[53].requires == (51, 52)
    assert events[123].requires == (120, 122)
    assert events[172].requires == (170, 171)
    assert events[174].requires == (159, 173)
    assert events[179].requires == (158, 169, 177, 178)
    assert events[189].requires == (143, 188)


def test_story_event_graph_is_acyclic_and_reaches_ending() -> None:
    events = load_story_events()
    order = topological_order(events)
    position = {event_id: index for index, event_id in enumerate(order)}

    assert len(order) == 225
    assert 225 in order
    for event_id, event in events.items():
        for requirement in event.requires:
            assert position[requirement] < position[event_id]


def test_ending_ancestor_closure_contains_parallel_required_branches() -> None:
    events = load_story_events()
    ancestors = ancestor_closure(events, 225)

    # Examples of branches that later merge into the Normal Ending chain.
    for required in (120, 122, 159, 170, 171, 178, 189, 224, 225):
        assert required in ancestors


def test_legal_next_events_respects_multi_parent_gate() -> None:
    events = load_story_events()

    only_120 = {event_id for event_id in range(1, 120)} | {120}
    assert 123 not in {
        event.chart_event_id for event in legal_next_events(events, only_120)
    }

    both = only_120 | {121, 122}
    assert 123 in {event.chart_event_id for event in legal_next_events(events, both)}
