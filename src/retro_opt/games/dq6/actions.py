from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DQ6ActionKind(StrEnum):
    """DQ6 route optimizationで扱うmacro actionの分類。

    frame-level inputは別層で扱い、ここでは全体routeへ価値を伝播させる単位を表す。
    """

    MOVE = "move"
    TALK = "talk"
    INSPECT = "inspect"
    PICKUP = "pickup"
    SKIP_PICKUP = "skip_pickup"
    USE_ITEM = "use_item"
    TRANSFER_ITEM = "transfer_item"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    BUY = "buy"
    SELL = "sell"
    REST = "rest"
    REVIVE = "revive"
    FIGHT = "fight"
    FLEE = "flee"
    FARM = "farm"
    CLASS_CHANGE = "class_change"
    ROUTE_BRANCH = "route_branch"


@dataclass(frozen=True, slots=True)
class DQ6MacroAction:
    id: str
    kind: DQ6ActionKind
    target: str | None = None
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
