from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Literal, Mapping

from retro_opt.games.dq6.state import DQ6State
from retro_opt.games.dq6.story_events import StoryEvent, legal_next_events, load_story_events
from retro_opt.games.dq6.story_feasibility import missing_story_event_requirements


SpatialStatus = Literal["reachable", "unreachable", "unchecked"]


@dataclass(frozen=True, slots=True)
class StoryFrontierEntry:
    """One dependency-frontier event with feasibility diagnostics.

    `missing_non_spatial` contains resource/capability/state-machine blockers.
    Spatial reachability is kept separate because the map/vehicle/path model is
    intentionally not inferred from the chart event dependency graph.
    """

    event: StoryEvent
    missing_non_spatial: tuple[str, ...]
    spatial_status: SpatialStatus

    @property
    def nonspatial_ready(self) -> bool:
        return not self.missing_non_spatial

    @property
    def ready(self) -> bool:
        return self.nonspatial_ready and self.spatial_status == "reachable"


def story_frontier(
    state: DQ6State,
    events: Mapping[int, StoryEvent] | None = None,
    *,
    reachable_places: Iterable[str] | None = None,
) -> tuple[StoryFrontierEntry, ...]:
    """Return the current story-event frontier with explicit blockers.

    Only chart events whose prerequisite chart-event IDs are complete enter the
    frontier.  Resource/capability requirements are then checked separately.

    If `reachable_places` is omitted, spatial status is `unchecked`; such an
    entry is deliberately *not* considered fully ready.  This fail-closed
    behavior prevents the progression solver from treating a dependency-legal
    event as physically reachable before the map/vehicle layer has proved it.
    """

    event_map = load_story_events() if events is None else events
    reachable = None if reachable_places is None else frozenset(reachable_places)

    entries: list[StoryFrontierEntry] = []
    for event in legal_next_events(event_map, state.completed_chart_events):
        missing = missing_story_event_requirements(state, event)
        if reachable is None:
            spatial_status: SpatialStatus = "unchecked"
        elif event.place in reachable:
            spatial_status = "reachable"
        else:
            spatial_status = "unreachable"

        entries.append(
            StoryFrontierEntry(
                event=event,
                missing_non_spatial=missing,
                spatial_status=spatial_status,
            )
        )

    return tuple(entries)


def nonspatial_ready_story_events(
    state: DQ6State,
    events: Mapping[int, StoryEvent] | None = None,
) -> tuple[StoryEvent, ...]:
    """Return dependency/resource/capability-ready events, ignoring geography.

    This is useful for diagnostics and for composing a later reachability
    oracle.  It must not be used as the final legal-action set.
    """

    return tuple(
        entry.event
        for entry in story_frontier(state, events)
        if entry.nonspatial_ready
    )


def ready_story_events(
    state: DQ6State,
    reachable_places: Iterable[str],
    events: Mapping[int, StoryEvent] | None = None,
) -> tuple[StoryEvent, ...]:
    """Return events legal under chart, non-spatial, and spatial gates."""

    return tuple(
        entry.event
        for entry in story_frontier(
            state,
            events,
            reachable_places=reachable_places,
        )
        if entry.ready
    )


def apply_story_event_completion(
    state: DQ6State,
    event: StoryEvent,
    *,
    destination_location: str | None = None,
) -> DQ6State:
    """Apply the irreversible chart-event completion marker.

    This function validates all non-spatial requirements but intentionally does
    not guess path reachability.  Callers that represent actual gameplay must
    obtain `event` from `ready_story_events()` (or perform an equivalent map
    reachability proof) before applying it.

    Event-specific item consumption, rewards, battle outcomes, temporary flags,
    and world unlocks remain explicit transition effects in their respective
    models; they are not fabricated from the event's free-form `effect` label.
    """

    if event.chart_event_id in state.completed_chart_events:
        raise ValueError(f"story event already completed: {event.chart_event_id}")

    missing = missing_story_event_requirements(state, event)
    if missing:
        raise ValueError(
            f"story event {event.chart_event_id} has unmet requirements: "
            + ", ".join(missing)
        )

    completed = state.completed_chart_events | {event.chart_event_id}
    updates: dict[str, object] = {"completed_chart_events": completed}
    if destination_location is not None:
        updates["location"] = destination_location
    return replace(state, **updates)
