from __future__ import annotations

import json
from pathlib import Path

from retro_opt.solver.value_iteration import solve_ssp
from retro_opt.synthetic.resource_route import (
    GOAL,
    START,
    ResourceDependencyEnv,
    ResourceRouteState,
    enumerate_reachable_states,
)


def run() -> dict[str, object]:
    env = ResourceDependencyEnv()
    states = enumerate_reachable_states(env)
    values, policy = solve_ssp(env, states=states, terminal_states=(GOAL,))

    checkpoints = [
        START,
        ResourceRouteState("gold_chest", has_shield=True),
        ResourceRouteState("town", has_shield=True, gold=50),
        ResourceRouteState("shop", has_shield=True, gold=50),
    ]

    boss_states = {
        "none": ResourceRouteState("boss"),
        "shield_only": ResourceRouteState("boss", has_shield=True),
        "potion_only": ResourceRouteState("boss", has_potion=True),
        "shield_and_potion": ResourceRouteState(
            "boss", has_shield=True, has_potion=True
        ),
    }

    return {
        "schema_version": "0.1",
        "experiment_id": "resource-dependency-toy-v0",
        "type": "solver-validation",
        "empirical_claim": False,
        "description": (
            "item pickup, gold pickup, sell/buy decisions and boss retry riskを"
            "同一state spaceで扱えるかを確認するsynthetic benchmark"
        ),
        "optimal_start_value_seconds": values[START],
        "optimal_decisions": [
            {
                "stage": state.stage,
                "has_shield": state.has_shield,
                "gold": state.gold,
                "has_potion": state.has_potion,
                "action": policy[state],
            }
            for state in checkpoints
        ],
        "boss_expected_remaining_seconds": {
            name: values[state] for name, state in boss_states.items()
        },
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
