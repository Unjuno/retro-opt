from retro_opt.games.dq6.state import DQ6State, PartyMemberState


def test_dq6_state_is_hashable_and_member_lookup_works() -> None:
    state = DQ6State(
        segment="early",
        location="amor_north_cave",
        party=(
            PartyMemberState("hero", hp=50, mp=10, exp=825, level=6),
            PartyMemberState("hassan", hp=70, mp=0, exp=700, level=6),
            PartyMemberState("mireille", hp=45, mp=18, exp=600, level=6),
        ),
        gold=1000,
        counters=(("small_medals", 7),),
    )

    assert state.member("hero").exp == 825
    assert state.counter("small_medals") == 7
    assert state.counter("missing_counter") == 0
    assert hash(state) == hash(state)


def test_state_tracks_bag_personal_items_stats_equipment_and_counters() -> None:
    protagonist = PartyMemberState(
        name="hero",
        hp=50,
        mp=10,
        exp=847,
        level=7,
        stats=(("strength", 20),),
        equipment=(("weapon", "blade_boomerang"),),
        personal_items=(("herb", 2),),
    )
    state = DQ6State(
        segment="amor_north",
        location="b2",
        party=(protagonist,),
        bag=(("wing", 1),),
        gold=410,
        counters=(("small_medals", 7), ("encounter_skill_count", 0)),
    )

    assert protagonist.stat("strength") == 20
    assert protagonist.equipped("weapon") == "blade_boomerang"
    assert state.bag_count("wing") == 1
    assert state.counter("small_medals") == 7
    assert state.owns("blade_boomerang")
    assert state.owns("herb")
    assert state.owns("wing")
    assert not state.owns("iron_shield")
