from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True, slots=True)
class ResourceDominanceLabel:
    """資源付きroute stateを安全寄りに比較するためのlabel。

    `exact_signature` は inventory layout / equipment / flags など、単調性をまだ
    証明していない状態をまとめたもの。ここが一致しないstate同士は支配判定しない。

    `monotone_resources` には「大きいほど悪化しない」と別途宣言できた値だけを入れる。
    例: 同じ他状態での gold、純粋な permanent stat increase など。
    """

    elapsed_seconds: float
    monotone_resources: tuple[float, ...]
    exact_signature: Hashable

    def __post_init__(self) -> None:
        if self.elapsed_seconds < 0.0:
            raise ValueError("elapsed_seconds must be non-negative")


def resource_dominates(
    left: ResourceDominanceLabel,
    right: ResourceDominanceLabel,
) -> bool:
    """leftがrightを安全に支配すると宣言できる場合のみTrue。"""

    if left.exact_signature != right.exact_signature:
        return False
    if len(left.monotone_resources) != len(right.monotone_resources):
        raise ValueError("monotone resource vectors must have the same length")

    time_weak = left.elapsed_seconds <= right.elapsed_seconds
    resources_weak = all(
        left_value >= right_value
        for left_value, right_value in zip(
            left.monotone_resources,
            right.monotone_resources,
            strict=True,
        )
    )
    if not (time_weak and resources_weak):
        return False

    return (
        left.elapsed_seconds < right.elapsed_seconds
        or any(
            left_value > right_value
            for left_value, right_value in zip(
                left.monotone_resources,
                right.monotone_resources,
                strict=True,
            )
        )
    )


def conservative_resource_frontier(
    labels: list[ResourceDominanceLabel],
) -> list[ResourceDominanceLabel]:
    """宣言済みの単調軸だけで安全に落とせるlabelを除去する。"""

    frontier: list[ResourceDominanceLabel] = []
    for index, candidate in enumerate(labels):
        if any(
            resource_dominates(other, candidate)
            for other_index, other in enumerate(labels)
            if other_index != index
        ):
            continue
        frontier.append(candidate)
    return frontier
