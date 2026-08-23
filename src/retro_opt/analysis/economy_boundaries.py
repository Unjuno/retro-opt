from __future__ import annotations

from collections.abc import Iterable


def total_inflow(inflows: Iterable[int]) -> int:
    values = tuple(inflows)
    if any(value < 0 for value in values):
        raise ValueError("inflows must be non-negative")
    return sum(values)


def minimum_starting_gold_for_spend(
    *,
    spend_gold: int,
    inflows: Iterable[int] = (),
) -> int:
    """既知inflowをすべて受け取る前提でspendを実行できる最小開始gold。"""

    if spend_gold < 0:
        raise ValueError("spend_gold must be non-negative")
    return max(0, spend_gold - total_inflow(inflows))


def starting_gold_window_for_post_spend_balance(
    *,
    spend_gold: int,
    inflows: Iterable[int] = (),
    max_post_spend_gold: int,
) -> tuple[int, int] | None:
    """spend可能かつ、支出後goldが指定上限以下になる開始gold範囲。

    すべてのinflowを支出前に得る単純な離散モデル。戻り値はinclusive。
    """

    if spend_gold < 0:
        raise ValueError("spend_gold must be non-negative")
    if max_post_spend_gold < 0:
        raise ValueError("max_post_spend_gold must be non-negative")

    inflow = total_inflow(inflows)
    minimum = max(0, spend_gold - inflow)
    maximum = spend_gold + max_post_spend_gold - inflow
    if maximum < minimum:
        return None
    return minimum, maximum


def post_spend_gold(
    *,
    starting_gold: int,
    spend_gold: int,
    inflows: Iterable[int] = (),
) -> int:
    if starting_gold < 0:
        raise ValueError("starting_gold must be non-negative")
    if spend_gold < 0:
        raise ValueError("spend_gold must be non-negative")
    result = starting_gold + total_inflow(inflows) - spend_gold
    if result < 0:
        raise ValueError("spend is infeasible for the supplied starting gold and inflows")
    return result
