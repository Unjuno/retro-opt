import pytest

from retro_opt.games.dq6.graph_codec import (
    decode_deterministic_effects,
    decode_requirements,
)


def test_decode_requirements() -> None:
    requirements = decode_requirements(
        {
            "min_gold": 720,
            "max_gold": 1000,
            "owned_items": {"iron_claw": 1},
            "min_counters": {"small_medals": 15},
            "required_resource_flags": ["shop_open"],
            "alive_members": ["hero"],
        }
    )

    assert requirements.min_gold == 720
    assert requirements.max_gold == 1000
    assert requirements.owned_items == (("iron_claw", 1),)
    assert requirements.min_counters == (("small_medals", 15),)
    assert requirements.required_resource_flags == frozenset({"shop_open"})
    assert requirements.alive_members == frozenset({"hero"})


def test_unknown_requirement_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported requirement fields"):
        decode_requirements({"owned_sellable_asset": True})


def test_decode_typed_deterministic_effects() -> None:
    decoded = decode_deterministic_effects(
        [
            "gold:+410",
            "gold:-100",
            "bag:iron_shield:+1",
            "counter:small_medals:+1",
            "mark:chest_collected",
            "unmark:chest_available",
        ]
    )

    assert decoded.effect.gold_delta == 310
    assert decoded.effect.bag_deltas == (("iron_shield", 1),)
    assert decoded.effect.counter_deltas == (("small_medals", 1),)
    assert decoded.effect.add_resource_flags == frozenset({"chest_collected"})
    assert decoded.effect.remove_resource_flags == frozenset({"chest_available"})
    assert decoded.unresolved == ()


def test_untyped_or_unknown_effects_are_not_silently_interpreted() -> None:
    decoded = decode_deterministic_effects(
        [
            "iron_shield:+1",
            "gold:+unknown:sale_value",
            "remove:selected_asset",
        ]
    )

    assert decoded.effect.gold_delta == 0
    assert [item.token for item in decoded.unresolved] == [
        "iron_shield:+1",
        "gold:+unknown:sale_value",
        "remove:selected_asset",
    ]
