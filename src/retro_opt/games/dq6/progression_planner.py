from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from retro_opt.games.dq6.state import DQ6State
from retro_opt.games.dq6.story_events import StoryEvent, load_story_events
from retro_opt.games.dq6.story_frontier import StoryFrontierEntry, story_frontier
from retro_opt.games.dq6.story_schedule import remaining_required_event_ids


@dataclass(frozen=True, slots=True)
class TargetStoryFrontier:
    """Current story frontier partitioned by relevance to selected targets.

    `outside_target_*` is intentionally not called "optional": an event can be
    unnecessary for an intermediate target while still being mandatory for the
    eventual Normal Ending, or valuable as a resource detour.  The global
    optimizer must remain free to explore those actions.
    """

    required_ready: tuple[StoryFrontierEntry, ...]
    required_blocked: tuple[StoryFrontierEntry, ...]
    outside_target_ready: tuple[StoryFrontierEntry, ...]
    outside_target_blocked: tuple[StoryFrontierEntry, ...]

    @property
    def all_ready(self) -> tuple[StoryFrontierEntry, ...]:
        return self.required_ready + self.outside_target_ready


def target_story_frontier(
    state: DQ6State,
    targets: Iterable[int],
    reachable_places: Iterable[str],
    events: Mapping[int, StoryEvent] | None = None,
) -> TargetStoryFrontier:
    """Partition fully composed frontier entries by target ancestry.

    This function does not prune outside-target events.  It labels them so a
    higher-level search can decide whether a detour is globally worthwhile.
    """

    event_map = load_story_events() if events is None else events
    target_required = remaining_required_event_ids(
        event_map,
        state.completed_chart_events,
        targets,
    )

    required_ready: list[StoryFrontierEntry] = []
    required_blocked: list[StoryFrontierEntry] = []
    outside_ready: list[StoryFrontierEntry] = []
    outside_blocked: list[StoryFrontierEntry] = []

    for entry in story_frontier(
        state,
        event_map,
        reachable_places=reachable_places,
    ):
        is_required = entry.event.chart_event_id in target_required
        if is_required and entry.ready:
            required_ready.append(entry)
        elif is_required:
            required_blocked.append(entry)
        elif entry.ready:
            outside_ready.append(entry)
        else:
            outside_blocked.append(entry)

    return TargetStoryFrontier(
        required_ready=tuple(required_ready),
        required_blocked=tuple(required_blocked),
        outside_target_ready=tuple(outside_ready),
        outside_target_blocked=tuple(outside_blocked),
    )
