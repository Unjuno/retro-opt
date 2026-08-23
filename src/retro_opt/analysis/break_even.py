from __future__ import annotations

from dataclasses import dataclass
from math import inf, isclose
from typing import Iterable


@dataclass(frozen=True, slots=True)
class XpOutcome:
    """追加戦闘1回で得るEXPの離散分布。"""

    probability: float
    xp_gain: int
    label: str = ""


def validate_outcomes(outcomes: Iterable[XpOutcome]) -> tuple[XpOutcome, ...]:
    values = tuple(outcomes)
    if not values:
        raise ValueError("at least one outcome is required")
    if any(x.probability < 0.0 for x in values):
        raise ValueError("probability must be non-negative")
    if any(x.xp_gain < 0 for x in values):
        raise ValueError("xp_gain must be non-negative")
    total = sum(x.probability for x in values)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"probabilities must sum to 1, got {total}")
    return values


def threshold_cross_probability(
    *,
    current_xp: int,
    target_xp: int,
    outcomes: Iterable[XpOutcome],
) -> float:
    """追加戦闘1回でtarget_xp以上へ到達する確率を返す。"""

    values = validate_outcomes(outcomes)
    if current_xp >= target_xp:
        return 1.0
    return sum(
        outcome.probability
        for outcome in values
        if current_xp + outcome.xp_gain >= target_xp
    )


def break_even_downstream_saving_seconds(
    *,
    net_encounter_cost_seconds: float,
    crossing_probability: float,
) -> float:
    """追加戦闘が得になるために必要なdownstream savingの損益分岐値。

    単純モデル:
      fight = immediate net cost C
      thresholdを跨いだ場合のみ downstream cost が B 秒減る

    期待差は C - q*B なので、fightが有利になる条件は B > C/q。
    q=0なら閾値到達に寄与しないため inf を返す。
    """

    if net_encounter_cost_seconds < 0.0:
        raise ValueError("net_encounter_cost_seconds must be non-negative")
    if not 0.0 <= crossing_probability <= 1.0:
        raise ValueError("crossing_probability must be in [0, 1]")
    if crossing_probability == 0.0:
        return inf
    return net_encounter_cost_seconds / crossing_probability


def metal_mixture_outcomes(
    *,
    metal_probability: float,
    metal_xp: int,
    normal_xp_values: Iterable[int],
) -> tuple[XpOutcome, ...]:
    """感度分析用の簡易EXP混合分布を作る。

    `metal_probability` は「Metalが画面に出る確率」ではなく、追加戦闘1回が
    `metal_xp` を実際に獲得するoutcomeになる確率として扱う。Metalは逃走し得るため、
    実ゲームでは一般に encounter appearance rate と kill / reward probability を
    分離して推定する必要がある。

    `normal_xp_values` は、非Metal reward outcome時に等確率と仮定する。これは
    実ゲームのencounter tableを表すものではなく、実測値が入るまでの仮説モデル専用。
    """

    if not 0.0 <= metal_probability <= 1.0:
        raise ValueError("metal_probability must be in [0, 1]")
    normal = tuple(normal_xp_values)
    if not normal:
        raise ValueError("normal_xp_values must not be empty")
    if metal_xp < 0 or any(x < 0 for x in normal):
        raise ValueError("xp values must be non-negative")

    outcomes: list[XpOutcome] = []
    if metal_probability > 0.0:
        outcomes.append(XpOutcome(metal_probability, metal_xp, "metal-reward"))

    normal_probability = 1.0 - metal_probability
    each = normal_probability / len(normal)
    outcomes.extend(
        XpOutcome(each, xp, f"normal:{xp}") for xp in normal if each > 0.0
    )
    return validate_outcomes(outcomes)


def metal_encounter_outcomes(
    *,
    metal_appearance_probability: float,
    metal_kill_probability_given_appearance: float,
    metal_xp: int,
    normal_xp_values: Iterable[int],
    failed_metal_xp: int = 0,
) -> tuple[XpOutcome, ...]:
    """Metalの出現と撃破成功を分離した感度分析用EXP分布。

    - Metal出現: `metal_appearance_probability`
    - 出現したMetalを倒してEXPを得る: `metal_kill_probability_given_appearance`
    - Metalが出なかった場合: `normal_xp_values` を等確率と仮定
    - Metal出現後に失敗した場合: `failed_metal_xp`

    お供を倒して得るEXP等を扱う場合は `failed_metal_xp` を実測値へ置換する。
    """

    if not 0.0 <= metal_appearance_probability <= 1.0:
        raise ValueError("metal_appearance_probability must be in [0, 1]")
    if not 0.0 <= metal_kill_probability_given_appearance <= 1.0:
        raise ValueError("metal_kill_probability_given_appearance must be in [0, 1]")
    normal = tuple(normal_xp_values)
    if not normal:
        raise ValueError("normal_xp_values must not be empty")
    if metal_xp < 0 or failed_metal_xp < 0 or any(x < 0 for x in normal):
        raise ValueError("xp values must be non-negative")

    success_probability = (
        metal_appearance_probability * metal_kill_probability_given_appearance
    )
    failure_probability = (
        metal_appearance_probability
        * (1.0 - metal_kill_probability_given_appearance)
    )
    no_metal_probability = 1.0 - metal_appearance_probability

    outcomes: list[XpOutcome] = []
    if success_probability > 0.0:
        outcomes.append(XpOutcome(success_probability, metal_xp, "metal-kill"))
    if failure_probability > 0.0:
        outcomes.append(
            XpOutcome(failure_probability, failed_metal_xp, "metal-failed")
        )

    each = no_metal_probability / len(normal)
    outcomes.extend(
        XpOutcome(each, xp, f"normal:{xp}") for xp in normal if each > 0.0
    )
    return validate_outcomes(outcomes)
