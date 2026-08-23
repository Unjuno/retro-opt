from retro_opt.solver.pareto import Scored, dominates, pareto_frontier


def test_dominance_with_mixed_directions() -> None:
    # timeは小さいほど良く、completion probabilityは大きいほど良い。
    assert dominates((40.0, 0.95), (45.0, 0.90), ("min", "max"))
    assert not dominates((40.0, 0.80), (45.0, 0.90), ("min", "max"))


def test_frontier_keeps_tradeoffs_and_drops_dominated_candidate() -> None:
    candidates = [
        Scored("fast-risky", (35.0, 0.70)),
        Scored("balanced", (40.0, 0.90)),
        Scored("slow-dominated", (45.0, 0.85)),
    ]

    frontier = pareto_frontier(candidates, ("min", "max"))

    assert [candidate.item for candidate in frontier] == [
        "fast-risky",
        "balanced",
    ]
