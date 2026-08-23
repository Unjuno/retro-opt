from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from retro_opt.games.dq6.feasibility import (
    ActionRequirements,
    EquipmentChange,
    ResourceEffect,
)
from retro_opt.games.dq6.state import DQ6State


ItemLocationKind = Literal["bag", "personal", "equipped"]


@dataclass(frozen=True, slots=True)
class SellableDefinition:
    item: str
    sale_value_gold: int

    def __post_init__(self) -> None:
        if not self.item:
            raise ValueError("item must be non-empty")
        if self.sale_value_gold < 0:
            raise ValueError("sale_value_gold must be non-negative")


@dataclass(frozen=True, slots=True)
class GeneratedResourceAction:
    id: str
    kind: str
    item: str
    location_kind: ItemLocationKind
    holder: str | None
    slot: str | None
    requirements: ActionRequirements
    effect: ResourceEffect


def generate_sale_actions(
    state: DQ6State,
    catalog: tuple[SellableDefinition, ...],
) -> tuple[GeneratedResourceAction, ...]:
    """現在のitem配置から、1個売却する具体的actionを生成する。

    同名itemがbag・個人所持・装備に複数存在する場合、それぞれ別actionにする。
    これにより売却後のinventory layout / equipment stateを曖昧にしない。
    """

    actions: list[GeneratedResourceAction] = []

    for definition in catalog:
        item = definition.item
        sale_value = definition.sale_value_gold

        bag_count = state.bag_count(item)
        if bag_count > 0:
            actions.append(
                GeneratedResourceAction(
                    id=f"sell:{item}:bag",
                    kind="sell",
                    item=item,
                    location_kind="bag",
                    holder=None,
                    slot=None,
                    requirements=ActionRequirements(owned_items=((item, 1),)),
                    effect=ResourceEffect(
                        gold_delta=sale_value,
                        bag_deltas=((item, -1),),
                    ),
                )
            )

        for member in state.party:
            personal_count = dict(member.personal_items).get(item, 0)
            if personal_count > 0:
                actions.append(
                    GeneratedResourceAction(
                        id=f"sell:{item}:personal:{member.name}",
                        kind="sell",
                        item=item,
                        location_kind="personal",
                        holder=member.name,
                        slot=None,
                        requirements=ActionRequirements(
                            personal_items=((member.name, item, 1),)
                        ),
                        effect=ResourceEffect(
                            gold_delta=sale_value,
                            personal_item_deltas=((member.name, item, -1),),
                        ),
                    )
                )

            for slot, equipped_item in member.equipment:
                if equipped_item != item:
                    continue
                actions.append(
                    GeneratedResourceAction(
                        id=f"sell:{item}:equipped:{member.name}:{slot}",
                        kind="sell",
                        item=item,
                        location_kind="equipped",
                        holder=member.name,
                        slot=slot,
                        requirements=ActionRequirements(
                            equipped_items=((member.name, slot, item),)
                        ),
                        effect=ResourceEffect(
                            gold_delta=sale_value,
                            equipment_changes=(EquipmentChange(member.name, slot, None),),
                        ),
                    )
                )

    return tuple(actions)
