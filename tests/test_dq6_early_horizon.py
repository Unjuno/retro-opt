from retro_opt.analysis.break_even import metal_mixture_outcomes
from retro_opt.games.dq6.early_segment import (
    GOAL,
    FarmingState,
    ThresholdFarmingEnv,
    enumerate_reachable_states,
)
from retro_opt.solver.value_iteration import solve_ssp


def _policy(exp: int, opportunities_left: int) -> str:
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
    start = FarmingState(exp=exp, opportunities_left=opportunities_left)
    states = enumerate_reachable_states(env, (start,))
    _, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))
    return policy[start]


def test_policy_can_change_with_remaining_opportunities() -> None:
    assert _policy(800, 1) == "skip"
    assert _policy(800, 3) == "fight"


def test_solver_can_defer_when_future_opportunity_is_equivalent() -> None:
    assert _policy(824, 1) == "fight"
    assert _policy(824, 3) == "skip"
