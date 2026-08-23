from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from retro_opt.games.dq6.feasibility import ActionRequirements, ResourceEffect


@dataclass(frozen=True, slots=True)
class UnresolvedGraphToken:
    token: str
    reason: str


@dataclass(frozen=True, slots=True)
class DecodedEffects:
    effect: ResourceEffect
    unresolved: tuple[UnresolvedGraphToken, ...] = ()


def _string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{field} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return tuple(value)


def _pair_tuple(value: Any, field: str) -> tuple[tuple[str, int], ...]:
    if value is None:
        return ()
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object mapping names to integers")
    pairs: list[tuple[str, int]] = []
    for name, count in value.items():
        if not isinstance(name, str) or not isinstance(count, int):
            raise ValueError(f"{field} must map strings to integers")
        pairs.append((name, count))
    return tuple(sorted(pairs))


def decode_requirements(raw: Mapping[str, Any] | None) -> ActionRequirements:
    """graph JSONのrequirementsをActionRequirementsへ変換する。

    未知fieldを黙って捨てない。schema migration漏れを検知するためValueErrorにする。
    """

    if raw is None:
        return ActionRequirements()

    supported = {
        "min_gold",
        "max_gold",
        "owned_items",
        "min_counters",
        "required_story_flags",
        "required_resource_flags",
        "forbidden_resource_flags",
        "alive_members",
    }
    unknown = set(raw) - supported
    if unknown:
        raise ValueError(f"unsupported requirement fields: {sorted(unknown)}")

    min_gold = raw.get("min_gold", 0)
    max_gold = raw.get("max_gold")
    if not isinstance(min_gold, int):
        raise ValueError("min_gold must be an integer")
    if max_gold is not None and not isinstance(max_gold, int):
        raise ValueError("max_gold must be an integer or null")

    return ActionRequirements(
        min_gold=min_gold,
        max_gold=max_gold,
        owned_items=_pair_tuple(raw.get("owned_items"), "owned_items"),
        min_counters=_pair_tuple(raw.get("min_counters"), "min_counters"),
        required_story_flags=frozenset(
            _string_tuple(raw.get("required_story_flags"), "required_story_flags")
        ),
        required_resource_flags=frozenset(
            _string_tuple(raw.get("required_resource_flags"), "required_resource_flags")
        ),
        forbidden_resource_flags=frozenset(
            _string_tuple(raw.get("forbidden_resource_flags"), "forbidden_resource_flags")
        ),
        alive_members=frozenset(
            _string_tuple(raw.get("alive_members"), "alive_members")
        ),
    )


def _parse_signed_integer(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


def decode_deterministic_effects(tokens: Sequence[str] | None) -> DecodedEffects:
    """現行graphの簡易effect tokenをResourceEffectへ変換する。

    Supported token forms:
    - `gold:+410`, `gold:-720`
    - `bag:iron_shield:+1`
    - `counter:small_medals:+1`
    - `mark:flag_name`
    - `unmark:flag_name`

    旧draftの `iron_shield:+1` のような型なしtokenは、itemかcounterか判定できないため
    unresolvedとして返す。`unknown:` を含むtokenも同様に保持し、勝手に数値化しない。
    """

    if tokens is None:
        return DecodedEffects(ResourceEffect())

    gold_delta = 0
    bag_deltas: list[tuple[str, int]] = []
    counter_deltas: list[tuple[str, int]] = []
    add_flags: set[str] = set()
    remove_flags: set[str] = set()
    unresolved: list[UnresolvedGraphToken] = []

    for token in tokens:
        if not isinstance(token, str):
            raise ValueError("deterministic effect tokens must be strings")

        if "unknown:" in token:
            unresolved.append(UnresolvedGraphToken(token, "contains unknown parameter"))
            continue

        if token.startswith("mark:"):
            flag = token.removeprefix("mark:")
            if not flag:
                raise ValueError("mark token requires a flag name")
            add_flags.add(flag)
            continue

        if token.startswith("unmark:"):
            flag = token.removeprefix("unmark:")
            if not flag:
                raise ValueError("unmark token requires a flag name")
            remove_flags.add(flag)
            continue

        parts = token.split(":")
        if len(parts) == 2 and parts[0] == "gold":
            delta = _parse_signed_integer(parts[1])
            if delta is None:
                unresolved.append(UnresolvedGraphToken(token, "gold delta is not numeric"))
            else:
                gold_delta += delta
            continue

        if len(parts) == 3 and parts[0] in {"bag", "counter"}:
            _, name, delta_text = parts
            delta = _parse_signed_integer(delta_text)
            if not name or delta is None:
                unresolved.append(UnresolvedGraphToken(token, "invalid typed resource delta"))
            elif parts[0] == "bag":
                bag_deltas.append((name, delta))
            else:
                counter_deltas.append((name, delta))
            continue

        unresolved.append(
            UnresolvedGraphToken(
                token,
                "untyped or unsupported deterministic effect token",
            )
        )

    return DecodedEffects(
        effect=ResourceEffect(
            gold_delta=gold_delta,
            bag_deltas=tuple(bag_deltas),
            counter_deltas=tuple(counter_deltas),
            add_resource_flags=frozenset(add_flags),
            remove_resource_flags=frozenset(remove_flags),
        ),
        unresolved=tuple(unresolved),
    )
