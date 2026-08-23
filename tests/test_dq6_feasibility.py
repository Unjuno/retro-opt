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


def test_owned_count_includes_bag_personal_and_equipped() -> None:
    state = make_state()
    assert owned_count(state, "herb") == 3
    assert owned_count(state, "scale_shield") == 1


def test_apply_resource_effect_can_model_purchase_and_seed_use() -> None:
    state = make_state()
    next_state = apply_resource_effect(
        state,
        ResourceEffect(
            gold_delta=-720,
            bag_deltas=(("iron_shield", 1),),
            stat_deltas=(("hassan", "max_hp", 5),),
            add_resource_flags=frozenset({"iron_shield_bought", "life_seed_used"}),
        ),
    )

    assert next_state.gold == 0
    assert next_state.bag_count("iron_shield") == 1
    assert next_state.member("hassan").stat("max_hp") == 5
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
