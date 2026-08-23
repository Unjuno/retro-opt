from retro_opt.analysis.break_even import metal_mixture_outcomes
from retro_opt.games.dq6.early_segment import (
    GOAL,
    FarmingState,
    ThresholdFarmingEnv,
    enumerate_reachable_states,
)
from retro_opt.solver.value_iteration import solve_ssp


def _solve_at_exp(exp: int) -> str:
    env = ThresholdFarmingEnv(
        target_exp=847,
        encounter_cost_seconds=10.0,
        downstream_penalty_seconds=30.0,
        xp_outcomes=metal_mixture_outcomes(
            metal_probability=0.05,
            metal_xp=1350,
            normal_xp_values=(19, 19, 21, 23, 24),
        ),
    )
    start = FarmingState(exp=exp, opportunities_left=1)
    states = enumerate_reachable_states(env, (start,))
    _, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))
    return policy[start]


def test_policy_skips_when_threshold_is_too_far() -> None:
    assert _solve_at_exp(800) == "skip"


def test_policy_fights_when_close_enough_to_threshold() -> None:
    assert _solve_at_exp(825) == "fight"


def test_policy_boundary_is_state_dependent() -> None:
    actions = {exp: _solve_at_exp(exp) for exp in range(800, 831)}
    assert actions[823] == "skip"
    assert actions[824] == "fight"
