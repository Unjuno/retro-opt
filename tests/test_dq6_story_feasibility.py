from dataclasses import replace

from retro_opt.games.dq6.state import DQ6State, PartyMemberState
from retro_opt.games.dq6.story_events import load_story_events
from retro_opt.games.dq6.story_feasibility import (
    is_story_event_ready,
    missing_story_event_requirements,
)


def _hero(**kwargs: object) -> PartyMemberState:
    base = dict(name="hero", hp=50, mp=20, exp=1000, level=10)
    base.update(kwargs)
    return PartyMemberState(**base)


def _state(**kwargs: object) -> DQ6State:
    base = dict(segment="test", location="test", party=(_hero(),))
    base.update(kwargs)
    return DQ6State(**base)


def test_ferry_ticket_event_checks_predecessor_and_gold() -> None:
    event = load_story_events()[44]

    state = _state(completed_chart_events=frozenset({43}), gold=149)
    assert missing_story_event_requirements(state, event) == ("gold>=150",)

    assert is_story_event_ready(replace(state, gold=150), event)


def test_moon_mirror_event_requires_all_four_orbs() -> None:
    event = load_story_events()[61]

    state = _state(
        completed_chart_events=frozenset({60}),
        event_counters=(("moon_mirror_orbs_destroyed", 3),),
    )
    assert "event_counter:moon_mirror_orbs_destroyed>=4" in missing_story_event_requirements(
        state, event
    )

    ready = replace(
        state,
        event_counters=(("moon_mirror_orbs_destroyed", 4),),
    )
    assert is_story_event_ready(ready, event)


def test_barbara_event_requires_dream_dew() -> None:
    event = load_story_events()[62]

    state = _state(completed_chart_events=frozenset({61}))
    assert "item:dream_dew" in missing_story_event_requirements(state, event)

    ready = replace(state, bag=(("dream_dew", 1),))
    assert is_story_event_ready(ready, event)


def test_magician_tower_event_requires_inpas_capability() -> None:
    event = load_story_events()[132]

    state = _state(completed_chart_events=frozenset({131}))
    assert "command:inpas" in missing_story_event_requirements(state, event)

    hero = replace(state.party[0], learned_commands=frozenset({"inpas"}))
    assert is_story_event_ready(replace(state, party=(hero,)), event)


def test_sacred_shrine_event_requires_four_legendary_items_equipped() -> None:
    event = load_story_events()[180]

    state = _state(completed_chart_events=frozenset({179}))
    missing = missing_story_event_requirements(state, event)
    assert "hero_equipped:ramias_sword" in missing
    assert "hero_equipped:orgo_armor" in missing
    assert "hero_equipped:sphida_shield" in missing
    assert "hero_equipped:sebas_helm" in missing

    hero = replace(
        state.party[0],
        equipment=(
            ("weapon", "ramias_sword"),
            ("armor", "orgo_armor"),
            ("shield", "sphida_shield"),
            ("helmet", "sebas_helm"),
        ),
    )
    assert is_story_event_ready(replace(state, party=(hero,)), event)


def test_tenma_tower_event_requires_ultimate_key_and_both_chart_parents() -> None:
    event = load_story_events()[189]

    state = _state(completed_chart_events=frozenset({188}))
    missing = missing_story_event_requirements(state, event)
    assert "chart_event:143" in missing

    # Event 189's external chart dependency captures the Ultimate Key event.
    # The key itself is also retained as a resource gate in the normalized row.
    state = replace(state, completed_chart_events=frozenset({143, 188}))
    assert "item:ultimate_key" in missing_story_event_requirements(state, event)

    assert is_story_event_ready(replace(state, bag=(("ultimate_key", 1),)), event)
