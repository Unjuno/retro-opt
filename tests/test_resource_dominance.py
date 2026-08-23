import pytest

from retro_opt.solver.resource_dominance import (
    ResourceDominanceLabel,
    conservative_resource_frontier,
    resource_dominates,
)


def test_more_monotone_resource_and_less_time_can_dominate() -> None:
    better = ResourceDominanceLabel(
        elapsed_seconds=10.0,
        monotone_resources=(1000.0, 50.0),
        exact_signature=("same-layout", "same-equipment"),
    )
    worse = ResourceDominanceLabel(
        elapsed_seconds=12.0,
        monotone_resources=(900.0, 50.0),
        exact_signature=("same-layout", "same-equipment"),
    )
    assert resource_dominates(better, worse)


def test_different_inventory_layout_is_not_pruned() -> None:
    fast_with_extra_item = ResourceDominanceLabel(
        elapsed_seconds=10.0,
        monotone_resources=(1000.0,),
        exact_signature=("layout:A",),
    )
    slow_without_extra_item = ResourceDominanceLabel(
        elapsed_seconds=12.0,
        monotone_resources=(900.0,),
        exact_signature=("layout:B",),
    )

    assert not resource_dominates(fast_with_extra_item, slow_without_extra_item)
    assert conservative_resource_frontier(
        [fast_with_extra_item, slow_without_extra_item]
    ) == [fast_with_extra_item, slow_without_extra_item]


def test_equal_label_does_not_strictly_dominate_itself() -> None:
    left = ResourceDominanceLabel(10.0, (100.0,), "same")
    right = ResourceDominanceLabel(10.0, (100.0,), "same")
    assert not resource_dominates(left, right)


def test_resource_vector_length_mismatch_is_error() -> None:
    left = ResourceDominanceLabel(10.0, (100.0,), "same")
    right = ResourceDominanceLabel(11.0, (100.0, 5.0), "same")
    with pytest.raises(ValueError):
        resource_dominates(left, right)
