from retro_opt.games.dq6.story_events import StoryEvent, load_story_events
from retro_opt.games.dq6.story_schedule import (
    dependency_window_frontier,
    enumerate_dependency_schedules,
    remaining_required_event_ids,
)


def test_exact_scheduler_enumerates_both_orders_of_a_diamond() -> None:
    events = {
        1: StoryEvent(1, "a", "start", "a"),
        2: StoryEvent(2, "b", "left", "b", (1,)),
        3: StoryEvent(3, "c", "right", "c", (1,)),
        4: StoryEvent(4, "d", "merge", "d", (2, 3)),
    }

    result = enumerate_dependency_schedules(events, {1}, {4}, max_schedules=10)

    assert not result.truncated
    assert set(result.schedules) == {(2, 3, 4), (3, 2, 4)}


def test_target_window_excludes_legal_but_nonancestor_detours() -> None:
    events = load_story_events()
    completed = frozenset(range(1, 143))

    remaining = remaining_required_event_ids(events, completed, {179})

    # Ultimate Key (143) is available after Mermaid Harp, but is not required
    # to obtain Ramias Sword (179), so it is outside this target skeleton.
    assert 143 not in remaining
    assert 179 in remaining


def test_legendary_equipment_window_exposes_parallel_branches() -> None:
    events = load_story_events()
    completed = frozenset(range(1, 143))
    remaining = remaining_required_event_ids(events, completed, {179})

    frontier = set(dependency_window_frontier(events, completed, remaining))

    # These are independent starts of the late-midgame branches that eventually
    # merge at event 179.  The scheduler must not impose the published chart's
    # textual order on them.
    assert frontier == {144, 159, 160, 170, 171, 178}


def test_schedule_search_is_bounded_without_hiding_truncation() -> None:
    events = {
        1: StoryEvent(1, "a", "start", "a"),
        2: StoryEvent(2, "b", "p2", "b", (1,)),
        3: StoryEvent(3, "c", "p3", "c", (1,)),
        4: StoryEvent(4, "d", "p4", "d", (1,)),
        5: StoryEvent(5, "e", "merge", "e", (2, 3, 4)),
    }

    result = enumerate_dependency_schedules(events, {1}, {5}, max_schedules=2)

    assert len(result.schedules) == 2
    assert result.truncated
    assert all(schedule[-1] == 5 for schedule in result.schedules)
