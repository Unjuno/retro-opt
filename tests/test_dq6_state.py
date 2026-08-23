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
    )

    assert state.member("hero").exp == 825
    assert hash(state) == hash(state)
