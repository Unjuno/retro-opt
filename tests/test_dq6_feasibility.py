import pytest

from retro_opt.games.dq6.feasibility import (
    ActionRequirements,
    EquipmentChange,
    ResourceEffect,
    apply_resource_effect,
    is_feasible,
    missing_requirements,
    owned_count,
)
from retro_opt.games.dq6.state import DQ6State, PartyMemberState


def make_state() -> DQ6State:
    return DQ6State(
        segment="early",
        location="amor",
        party=(
            PartyMemberState(
                "hero",
                hp=50,
                mp=10,
                exp=825,
                level=6,
                stats=(("max_hp", 50),),
                equipment=(("shield", "scale_shield"),),
                personal_items=(("herb", 1),),
            ),
            PartyMemberState("hassan", hp=70, mp=0, exp=700, level=6),
        ),
        bag=(("herb", 2),),
        gold=720,
        counters=(("small_medals", 7),),
        story_flags=frozenset({"amor_shop_open"}),
        resource_flags=frozenset({"iron_claw_collected"}),
    )


def test_requirements_are_feasibility_not_reward() -> None:
    state = make_state()
    buy = ActionRequirements(
        min_gold=720,
        required_story_flags=frozenset({"amor_shop_open"}),
    )
    assert is_feasible(state, buy)

    too_expensive = ActionRequirements(min_gold=721)
    assert not is_feasible(state, too_expensive)
    assert missing_requirements(state, too_expensive) == ("gold>=721",)


def test_upper_bound_gold_can_gate_recovery_branch() -> None:
    state = make_state()
    low_gold_branch = ActionRequirements(max_gold=140)
    assert not is_feasible(state, low_gold_branch)
    assert missing_requirements(state, low_gold_branch) == ("gold<=140",)


def test_counter_threshold_can_gate_cumulative_reward_action() -> None:
    state = make_state()
    medal70 = ActionRequirements(min_counters=(("small_medals", 70),))
    assert not is_feasible(state, medal70)
    assert missing_requirements(state, medal70) == ("counter:small_medals>=70",)


def test_invalid_gold_interval_is_rejected() -> None:
    with pytest.raises(ValueError):
        ActionRequirements(min_gold=200, max_gold=100)


def test_owned_count_includes_bag_personal_and_equipped() -> None:
    state = make_state()
    assert owned_count(state, "herb") == 3
    assert owned_count(state, "scale_shield") == 1


def test_apply_resource_effect_can_model_purchase_seed_and_medal_pickup() -> None:
    state = make_state()
    next_state = apply_resource_effect(
        state,
        ResourceEffect(
            gold_delta=-720,
            bag_deltas=(("iron_shield", 1),),
            stat_deltas=(("hassan", "max_hp", 5),),
            counter_deltas=(("small_medals", 1),),
            add_resource_flags=frozenset({"iron_shield_bought", "life_seed_used"}),
        ),
    )

    assert next_state.gold == 0
    assert next_state.bag_count("iron_shield") == 1
    assert next_state.member("hassan").stat("max_hp") == 5
    assert next_state.counter("small_medals") == 8
    assert "iron_shield_bought" in next_state.resource_flags


def test_equipment_change_is_explicit_and_does_not_guess_item_movement() -> None:
    state = make_state()
    next_state = apply_resource_effect(
        state,
        ResourceEffect(
            equipment_changes=(EquipmentChange("hero", "shield", "iron_shield"),),
        ),
    )

    assert next_state.member("hero").equipped("shield") == "iron_shield"
    # 装備変更に伴うbag/personal item移動は呼び出し側が明示する設計。
    assert next_state.bag == state.bag


def test_negative_resource_count_is_rejected() -> None:
    state = make_state()
    with pytest.raises(ValueError):
        apply_resource_effect(
            state,
            ResourceEffect(bag_deltas=(("magic_water", -1),)),
        )


def test_negative_counter_is_rejected() -> None:
    state = make_state()
    with pytest.raises(ValueError):
        apply_resource_effect(
            state,
            ResourceEffect(counter_deltas=(("small_medals", -8),)),
        )
