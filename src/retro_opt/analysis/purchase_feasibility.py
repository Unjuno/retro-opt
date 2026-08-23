from __future__ import annotations


def max_units_affordable(*, gold: int, unit_price: int) -> int:
    """所持金だけを制約とした購入可能個数を返す。"""

    if gold < 0:
        raise ValueError("gold must be non-negative")
    if unit_price <= 0:
        raise ValueError("unit_price must be positive")
    return gold // unit_price


def pickup_changes_affordability(
    *,
    starting_gold: int,
    pickup_gold: int,
    unit_price: int,
    target_units: int,
) -> bool:
    """gold pickupがtarget_unitsの購入可否を変えるならTrue。"""

    if pickup_gold < 0:
        raise ValueError("pickup_gold must be non-negative")
    if target_units <= 0:
        raise ValueError("target_units must be positive")

    before = max_units_affordable(gold=starting_gold, unit_price=unit_price)
    after = max_units_affordable(
        gold=starting_gold + pickup_gold,
        unit_price=unit_price,
    )
    return before < target_units <= after


def starting_gold_window_where_pickup_unlocks(
    *,
    pickup_gold: int,
    unit_price: int,
    target_units: int,
) -> tuple[int, int] | None:
    """pickupによってtarget_units購入が初めて可能になるstarting goldの整数範囲。

    戻り値は inclusive な `(min_gold, max_gold)`。
    pickupだけでは必要額へ届かないstarting goldが存在しない場合はNoneではなく、
    自然に空区間となるケースのみNoneを返す。
    """

    if pickup_gold < 0:
        raise ValueError("pickup_gold must be non-negative")
    if unit_price <= 0:
        raise ValueError("unit_price must be positive")
    if target_units <= 0:
        raise ValueError("target_units must be positive")

    required = unit_price * target_units
    minimum = max(0, required - pickup_gold)
    maximum = required - 1
    if minimum > maximum:
        return None
    return minimum, maximum
