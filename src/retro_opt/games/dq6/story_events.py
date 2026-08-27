from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Mapping


DEFAULT_STORY_EVENT_FILES = (
    "story_chart_events_001_081.json",
    "story_chart_events_082_149.json",
    "story_chart_events_150_225.json",
)


@dataclass(frozen=True, slots=True)
class StoryEvent:
    chart_event_id: int
    place: str
    trigger: str
    effect: str
    requires: tuple[int, ...] = ()
    raw: Mapping[str, object] | None = None


def default_data_dir() -> Path:
    """Return the repository-local DQ6 data directory.

    The default is intended for the research repository/test environment.  A
    packaged application may pass an explicit data_dir to load_story_events().
    """

    return Path(__file__).resolve().parents[4] / "games" / "sfc" / "dq6" / "data"


def load_story_events(data_dir: Path | str | None = None) -> dict[int, StoryEvent]:
    base = Path(data_dir) if data_dir is not None else default_data_dir()
    events: dict[int, StoryEvent] = {}

    for filename in DEFAULT_STORY_EVENT_FILES:
        payload = json.loads((base / filename).read_text(encoding="utf-8"))
        for row in payload["events"]:
            event_id = int(row["chart_event_id"])
            if event_id in events:
                raise ValueError(f"duplicate story event id: {event_id}")
            events[event_id] = StoryEvent(
                chart_event_id=event_id,
                place=str(row["place"]),
                trigger=str(row["trigger"]),
                effect=str(row["effect"]),
                requires=tuple(int(value) for value in row.get("requires", ())),
                raw=row,
            )

    return events


def validate_story_events(
    events: Mapping[int, StoryEvent],
    *,
    expected_ids: Iterable[int] | None = range(1, 226),
) -> tuple[str, ...]:
    errors: list[str] = []
    ids = set(events)

    if expected_ids is not None:
        expected = set(expected_ids)
        missing = sorted(expected - ids)
        extra = sorted(ids - expected)
        if missing:
            errors.append(f"missing ids: {missing}")
        if extra:
            errors.append(f"unexpected ids: {extra}")

    for event_id, event in sorted(events.items()):
        for requirement in event.requires:
            if requirement not in ids:
                errors.append(
                    f"event {event_id} references unknown prerequisite {requirement}"
                )
            if requirement == event_id:
                errors.append(f"event {event_id} depends on itself")

    try:
        topological_order(events)
    except ValueError as exc:
        errors.append(str(exc))

    return tuple(errors)


def children_by_event(events: Mapping[int, StoryEvent]) -> dict[int, tuple[int, ...]]:
    children: dict[int, list[int]] = {event_id: [] for event_id in events}
    for event_id, event in events.items():
        for requirement in event.requires:
            if requirement in children:
                children[requirement].append(event_id)
    return {event_id: tuple(sorted(values)) for event_id, values in children.items()}


def topological_order(events: Mapping[int, StoryEvent]) -> tuple[int, ...]:
    """Return a topological order and reject cyclic dependency data."""

    indegree = {event_id: 0 for event_id in events}
    children = {event_id: [] for event_id in events}

    for event_id, event in events.items():
        for requirement in event.requires:
            if requirement not in events:
                continue
            indegree[event_id] += 1
            children[requirement].append(event_id)

    ready = sorted(event_id for event_id, degree in indegree.items() if degree == 0)
    result: list[int] = []

    while ready:
        event_id = ready.pop(0)
        result.append(event_id)
        for child in sorted(children[event_id]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
                ready.sort()

    if len(result) != len(events):
        cyclic = sorted(event_id for event_id, degree in indegree.items() if degree > 0)
        raise ValueError(f"story event dependency cycle detected: {cyclic}")

    return tuple(result)


def ancestor_closure(
    events: Mapping[int, StoryEvent], target_event_id: int
) -> frozenset[int]:
    """All chart events required by target_event_id, including the target."""

    if target_event_id not in events:
        raise KeyError(target_event_id)

    result: set[int] = set()
    stack = [target_event_id]
    while stack:
        event_id = stack.pop()
        if event_id in result:
            continue
        result.add(event_id)
        stack.extend(events[event_id].requires)
    return frozenset(result)


def legal_next_events(
    events: Mapping[int, StoryEvent], completed: Iterable[int]
) -> tuple[StoryEvent, ...]:
    """Return dependency-legal next chart events.

    This checks chart-event prerequisites only.  Resource, capability,
    location, temporary-state and human-observability gates are evaluated by
    higher-level DQ6 feasibility code.
    """

    completed_set = frozenset(completed)
    legal = [
        event
        for event_id, event in events.items()
        if event_id not in completed_set
        and all(requirement in completed_set for requirement in event.requires)
    ]
    return tuple(sorted(legal, key=lambda event: event.chart_event_id))
