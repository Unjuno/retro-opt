from retro_opt.analysis.sale_options import SellableAsset, enumerate_feasible_sale_subsets


ASSETS = (
    SellableAsset("iron_claw", 525),
    SellableAsset("scale_shield", 135),
)


def test_both_assets_required_at_low_starting_gold() -> None:
    results = enumerate_feasible_sale_subsets(
        starting_gold=370,
        fixed_inflow_gold=410,
        spend_gold=1440,
        assets=ASSETS,
    )
    assert [result.sold_asset_ids for result in results] == [
        ("iron_claw", "scale_shield"),
    ]


def test_iron_claw_alone_can_be_sold_at_middle_gold() -> None:
    results = enumerate_feasible_sale_subsets(
        starting_gold=505,
        fixed_inflow_gold=410,
        spend_gold=1440,
        assets=ASSETS,
    )
    assert ("iron_claw",) in [result.sold_asset_ids for result in results]
    assert ("scale_shield",) not in [result.sold_asset_ids for result in results]


def test_scale_shield_can_preserve_iron_claw_at_higher_gold() -> None:
    results = enumerate_feasible_sale_subsets(
        starting_gold=895,
        fixed_inflow_gold=410,
        spend_gold=1440,
        assets=ASSETS,
    )
    by_sold = {result.sold_asset_ids: result for result in results}
    assert ("scale_shield",) in by_sold
    assert by_sold[("scale_shield",)].retained_asset_ids == ("iron_claw",)


def test_no_sale_required_at_1030_with_410g_pickup() -> None:
    results = enumerate_feasible_sale_subsets(
        starting_gold=1030,
        fixed_inflow_gold=410,
        spend_gold=1440,
        assets=ASSETS,
    )
    by_sold = {result.sold_asset_ids: result for result in results}
    assert () in by_sold
    assert by_sold[()].retained_asset_ids == ("iron_claw", "scale_shield")
