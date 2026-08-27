from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from retro_opt.games.dq6.story_events import StoryEvent, ancestor_closure


@dataclass(frozen=True, slots=True)
class DependencyScheduleSearchResult:
    """Finite prefix of exact topological schedules for a target event set."""

    schedules: tuple[tuple[int, ...], ...]
    truncated: bool
    nodes_expanded: int


def remaining_required_event_ids(
    events: Mapping[int, StoryEvent],
    completed: Iterable[int],
    targets: Iterable[int],
) -> frozenset[int]:
    """Return unfinished chart events required to reach all `targets`.

    The result is the union of ancestor closures minus already completed events.
    Events that are not ancestors of a target are intentionally excluded, even
    if they are currently dependency-legal.  This lets a higher-level optimizer
    distinguish mandatory progression from optional/resource detours.
    """

    completed_set = frozenset(completed)
    required: set[int] = set()
    target_ids = tuple(targets)
    if not target_ids:
        return frozenset()

    for target in target_ids:
        required.update(ancestor_closure(events, target))

    return frozenset(required - completed_set)


def dependency_window_frontier(
    events: Mapping[int, StoryEvent],
    completed: Iterable[int],
    remaining: Iterable[int],
) -> tuple[int, ...]:
    """Return dependency-legal events inside a target-specific remaining set."""

    completed_set = frozenset(completed)
    remaining_set = frozenset(remaining)

    ready = [
        event_id
        for event_id in remaining_set
        if all(requirement in completed_set for requirement in events[event_id].requires)
    ]
    return tuple(sorted(ready))


def enumerate_dependency_schedules(
    events: Mapping[int, StoryEvent],
    completed: Iterable[int],
    targets: Iterable[int],
    *,
    max_schedules: int = 100,
) -> DependencyScheduleSearchResult:
    """Enumerate exact dependency-valid event orders up to `max_schedules`.

    This search uses no heuristic score and performs no reward shaping.  It is
    only the combinatorial progression skeleton.  Travel, resources, battles,
    stochastic outcomes, and dominance pruning belong to higher layers.

    The result is deliberately bounded because the number of topological orders
    can grow exponentially.  `truncated=True` means at least one additional
    valid schedule existed beyond the returned prefix.
    """

    if max_schedules <= 0:
        raise ValueError("max_schedules must be positive")

    completed_start = frozenset(completed)
    remaining_start = remaining_required_event_ids(events, completed_start, targets)
    if not remaining_start:
        return DependencyScheduleSearchResult(((),), False, 0)

    schedules: list[tuple[int, ...]] = []
    nodes_expanded = 0
    truncated = False

    def visit(
        completed_now: frozenset[int],
        remaining_now: frozenset[int],
        prefix: tuple[int, ...],
    ) -> None:
        nonlocal nodes_expanded, truncated

        if truncated:
            return
        if not remaining_now:
            schedules.append(prefix)
            if len(schedules) > max_schedules:
                schedules.pop()
                truncated = True
            return

        frontier = dependency_window_frontier(events, completed_now, remaining_now)
        if not frontier:
            raise ValueError(
                "target dependency window is blocked; completed set does not "
                "satisfy an external prerequisite"
            )

        nodes_expanded += 1
        for event_id in frontier:
            if truncated:
                return
            visit(
                completed_now | {event_id},
                remaining_now - {event_id},
                prefix + (event_id,),
            )

    visit(completed_start, remaining_start, ())
    return DependencyScheduleSearchResult(tuple(schedules), truncated, nodes_expanded)
