from retro_opt.analysis.break_even import metal_mixture_outcomes
from retro_opt.games.dq6.early_segment import (
    GOAL,
    FarmingState,
    ThresholdFarmingEnv,
    enumerate_reachable_states,
)
from retro_opt.solver.action_values import action_values
from retro_opt.solver.value_iteration import solve_ssp


def test_action_values_expose_policy_margin() -> None:
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
    start = FarmingState(exp=825, opportunities_left=1)
    states = enumerate_reachable_states(env, (start,))
    values, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))
    q = action_values(env, start, values)

    assert policy[start] == "fight"
    assert q["fight"] < q["skip"]
    assert q["skip"] == 30.0
