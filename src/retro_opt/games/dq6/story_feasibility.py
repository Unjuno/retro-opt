from __future__ import annotations

from retro_opt.games.dq6.state import DQ6State
from retro_opt.games.dq6.story_events import StoryEvent


_COMMAND_ALIASES = {
    "inpas_for_tower_entry": "inpas",
}


def missing_story_event_requirements(
    state: DQ6State,
    event: StoryEvent,
) -> tuple[str, ...]:
    """Return unmet non-spatial requirements for a normalized story event.

    Dependency flags, known key resources, simple party capabilities, and
    event counters are checked here.  Location/path reachability and complex
    minigame/battle policies remain separate submodels.

    Unknown capability keys fail closed: the event is not declared legal
    until a dedicated model knows how to evaluate the condition.
    """

    missing: list[str] = []

    for requirement in event.requires:
        if requirement not in state.completed_chart_events:
            missing.append(f"chart_event:{requirement}")

    raw = event.raw or {}

    resource_requirements = raw.get("resource_requirements", {})
    if isinstance(resource_requirements, dict):
        min_gold = resource_requirements.get("gold")
        if isinstance(min_gold, int) and state.gold < min_gold:
            missing.append(f"gold>={min_gold}")

    capability_requirements = raw.get("capability_requirements", {})
    if isinstance(capability_requirements, dict):
        for key, value in capability_requirements.items():
            if key == "item" and isinstance(value, str):
                if not state.owns(value):
                    missing.append(f"item:{value}")
            elif key == "command" and isinstance(value, str):
                command = _COMMAND_ALIASES.get(value, value)
                if not state.party_knows(command):
                    missing.append(f"command:{command}")
            elif key == "party_member" and isinstance(value, str):
                try:
                    state.member(value)
                except KeyError:
                    missing.append(f"party_member:{value}")
            elif key == "hero_equipment" and isinstance(value, list):
                try:
                    hero = state.member("hero")
                except KeyError:
                    missing.append("party_member:hero")
                    continue
                equipped = frozenset(dict(hero.equipment).values())
                for item in value:
                    if isinstance(item, str) and item not in equipped:
                        missing.append(f"hero_equipped:{item}")
            else:
                # Example: Best Dresser rank requirements.  Do not silently
                # reduce these to a single stat check because participant sex,
                # equipment set bonuses and per-rank restrictions matter.
                missing.append(f"dedicated_capability_model:{key}")

    state_machine = raw.get("state_machine", {})
    if isinstance(state_machine, dict):
        counter = state_machine.get("counter")
        target = state_machine.get("target")
        if isinstance(counter, str) and isinstance(target, int):
            if state.event_counter(counter) < target:
                missing.append(f"event_counter:{counter}>={target}")

    return tuple(missing)


def is_story_event_ready(state: DQ6State, event: StoryEvent) -> bool:
    return not missing_story_event_requirements(state, event)
