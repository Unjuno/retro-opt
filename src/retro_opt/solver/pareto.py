from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence, TypeVar

T = TypeVar("T")
Direction = Literal["min", "max"]


@dataclass(frozen=True, slots=True)
class Scored:
    item: T
    values: tuple[float, ...]


def dominates(
    left: Sequence[float],
    right: Sequence[float],
    directions: Sequence[Direction],
) -> bool:
    """leftがrightをPareto支配するならTrue。

    全軸でleftがright以上に良く、少なくとも1軸で厳密に良いことを要求する。
    """

    if len(left) != len(right) or len(left) != len(directions):
        raise ValueError("value vectors and directions must have the same length")

    weakly_better = True
    strictly_better = False

    for l_value, r_value, direction in zip(left, right, directions, strict=True):
        if direction == "min":
            if l_value > r_value:
                weakly_better = False
                break
            strictly_better |= l_value < r_value
        elif direction == "max":
            if l_value < r_value:
                weakly_better = False
                break
            strictly_better |= l_value > r_value
        else:
            raise ValueError(f"unknown direction: {direction!r}")

    return weakly_better and strictly_better


def pareto_frontier(
    candidates: Iterable[Scored[T]],
    directions: Sequence[Direction],
) -> list[Scored[T]]:
    """非支配候補だけを入力順を保って返す。"""

    items = list(candidates)
    frontier: list[Scored[T]] = []

    for index, candidate in enumerate(items):
        if any(
            dominates(other.values, candidate.values, directions)
            for other_index, other in enumerate(items)
            if other_index != index
        ):
            continue
        frontier.append(candidate)

    return frontier
