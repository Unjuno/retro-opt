from __future__ import annotations

from collections.abc import Iterable


def remaining_to_threshold(*, current: int, threshold: int) -> int:
    if current < 0:
        raise ValueError("current must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    return max(0, threshold - current)


def threshold_debt_vector(
    *,
    current: int,
    thresholds: Iterable[int],
) -> tuple[tuple[int, int], ...]:
    """各累積thresholdまであと何個必要かを返す。"""

    values = tuple(sorted(set(thresholds)))
    if any(value < 0 for value in values):
        raise ValueError("thresholds must be non-negative")
    return tuple(
        (threshold, remaining_to_threshold(current=current, threshold=threshold))
        for threshold in values
    )


def pickup_reduces_threshold_debt(
    *,
    current: int,
    pickup_count: int,
    thresholds: Iterable[int],
) -> tuple[tuple[int, int], ...]:
    """pickupで将来必要数が何個減るかをthresholdごとに返す。

    戻り値は `(threshold, reduction)`。すでに到達済みのthresholdは0になる。
    """

    if pickup_count < 0:
        raise ValueError("pickup_count must be non-negative")

    before = dict(threshold_debt_vector(current=current, thresholds=thresholds))
    after = dict(
        threshold_debt_vector(
            current=current + pickup_count,
            thresholds=thresholds,
        )
    )
    return tuple(
        (threshold, before[threshold] - after[threshold])
        for threshold in sorted(before)
    )
