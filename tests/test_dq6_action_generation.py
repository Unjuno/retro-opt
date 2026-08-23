from retro_opt.games.dq6.action_generation import (
    SellableDefinition,
    generate_sale_actions,
)
from retro_opt.games.dq6.feasibility import apply_resource_effect, is_feasible
from retro_opt.games.dq6.state import DQ6State, PartyMemberState


def make_state() -> DQ6State:
    return DQ6State(
        segment="post_horror",
        location="amor_shop",
        party=(
            PartyMemberState(
                "hero",
                hp=60,
                mp=8,
                exp=1000,
                level=7,
                personal_items=(("iron_claw", 1),),
                equipment=(("shield", "scale_shield"),),
            ),
            PartyMemberState("hassan", hp=80, mp=0, exp=900, level=7),
        ),
        bag=(("iron_claw", 1),),
        gold=400,
    )


def test_sale_actions_are_generated_per_item_location() -> None:
    actions = generate_sale_actions(
        make_state(),
        (
            SellableDefinition("iron_claw", 525),
            SellableDefinition("scale_shield", 135),
        ),
    )

    assert [action.id for action in actions] == [
        "sell:iron_claw:bag",
        "sell:iron_claw:personal:hero",
        "sell:scale_shield:equipped:hero:shield",
    ]


def test_generated_sale_effect_removes_exact_source_and_adds_gold() -> None:
    state = make_state()
    actions = {action.id: action for action in generate_sale_actions(
        state,
        (
            SellableDefinition("iron_claw", 525),
            SellableDefinition("scale_shield", 135),
        ),
    )}

    personal_sale = actions["sell:iron_claw:personal:hero"]
    assert is_feasible(state, personal_sale.requirements)
    after_personal = apply_resource_effect(state, personal_sale.effect)
    assert after_personal.gold == 925
    assert dict(after_personal.member("hero").personal_items).get("iron_claw", 0) == 0
    assert after_personal.bag_count("iron_claw") == 1

    shield_sale = actions["sell:scale_shield:equipped:hero:shield"]
    assert is_feasible(state, shield_sale.requirements)
    after_shield = apply_resource_effect(state, shield_sale.effect)
    assert after_shield.gold == 535
    assert after_shield.member("hero").equipped("shield") is None


def test_missing_catalog_item_generates_no_action() -> None:
    actions = generate_sale_actions(
        make_state(),
        (SellableDefinition("bamboo_spear", 37),),
    )
    assert actions == ()
