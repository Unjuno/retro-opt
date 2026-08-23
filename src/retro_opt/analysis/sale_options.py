from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class SellableAsset:
    id: str
    sale_value_gold: int

    def __post_init__(self) -> None:
        if self.sale_value_gold < 0:
            raise ValueError("sale_value_gold must be non-negative")


@dataclass(frozen=True, slots=True)
class SaleSubsetResult:
    sold_asset_ids: tuple[str, ...]
    retained_asset_ids: tuple[str, ...]
    sale_gold: int
    post_purchase_gold: int


def enumerate_feasible_sale_subsets(
    *,
    starting_gold: int,
    fixed_inflow_gold: int,
    spend_gold: int,
    assets: Iterable[SellableAsset],
) -> tuple[SaleSubsetResult, ...]:
    """purchaseを成立させるsell subsetを全列挙する。

    combat value等は評価せず、売却したassetと保持したassetをそのまま返す。
    """

    if starting_gold < 0 or fixed_inflow_gold < 0 or spend_gold < 0:
        raise ValueError("gold values must be non-negative")

    values = tuple(assets)
    results: list[SaleSubsetResult] = []
    ids = tuple(asset.id for asset in values)

    for count in range(len(values) + 1):
        for sold_indexes in combinations(range(len(values)), count):
            sold_index_set = set(sold_indexes)
            sold = tuple(values[index] for index in sold_indexes)
            sale_gold = sum(asset.sale_value_gold for asset in sold)
            available = starting_gold + fixed_inflow_gold + sale_gold
            if available < spend_gold:
                continue

            sold_ids = tuple(asset.id for asset in sold)
            retained_ids = tuple(
                ids[index]
                for index in range(len(values))
                if index not in sold_index_set
            )
            results.append(
                SaleSubsetResult(
                    sold_asset_ids=sold_ids,
                    retained_asset_ids=retained_ids,
                    sale_gold=sale_gold,
                    post_purchase_gold=available - spend_gold,
                )
            )

    return tuple(results)
