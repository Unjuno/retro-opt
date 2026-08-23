from __future__ import annotations

from dataclasses import dataclass, replace

from retro_opt.games.dq6.state import DQ6State, PartyMemberState


@dataclass(frozen=True, slots=True)
class ActionRequirements:
    """Macro action を選択可能にするための離散的な前提条件。

    ここでは「持っていないと罰点」のような reward shaping は行わない。
    条件を満たさない action は legal action set から外すために使う。
    HP/MP や battle-specific な連続値条件は、必要に応じて別の policy/model 層で扱う。
    """

    min_gold: int = 0
    max_gold: int | None = None
    owned_items: tuple[tuple[str, int], ...] = ()
    required_story_flags: frozenset[str] = frozenset()
    required_resource_flags: frozenset[str] = frozenset()
    forbidden_resource_flags: frozenset[str] = frozenset()
    alive_members: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.min_gold < 0:
            raise ValueError("min_gold must be non-negative")
        if self.max_gold is not None:
            if self.max_gold < 0:
                raise ValueError("max_gold must be non-negative")
            if self.max_gold < self.min_gold:
                raise ValueError("max_gold must be >= min_gold")
        if any(count <= 0 for _, count in self.owned_items):
            raise ValueError("owned item counts must be positive")


@dataclass(frozen=True, slots=True)
class EquipmentChange:
    member: str
    slot: str
    item: str | None


@dataclass(frozen=True, slots=True)
class ResourceEffect:
    """Macro action 後に確定的に生じる資源変化。

    `personal_item_deltas` は `(member, item, delta)`、`stat_deltas` は
    `(member, stat, delta)`。装備の付け外しに伴う item 移動は自動推論せず、
    呼び出し側が明示する。これは DQ6 の所持位置・メニュー順序を勝手に
    書き換えないためである。
    """

    gold_delta: int = 0
    bag_deltas: tuple[tuple[str, int], ...] = ()
    personal_item_deltas: tuple[tuple[str, str, int], ...] = ()
    stat_deltas: tuple[tuple[str, str, int], ...] = ()
    equipment_changes: tuple[EquipmentChange, ...] = ()
    add_resource_flags: frozenset[str] = frozenset()
    remove_resource_flags: frozenset[str] = frozenset()


def owned_count(state: DQ6State, item: str) -> int:
    """袋・個人所持・装備中を合算した item 数を返す。"""

    count = state.bag_count(item)
    for member in state.party:
        count += dict(member.personal_items).get(item, 0)
        count += sum(1 for _, equipped in member.equipment if equipped == item)
    return count


def missing_requirements(
    state: DQ6State,
    requirements: ActionRequirements,
) -> tuple[str, ...]:
    """満たしていない前提条件を、デバッグ可能な文字列として返す。"""

    missing: list[str] = []

    if state.gold < requirements.min_gold:
        missing.append(f"gold>={requirements.min_gold}")
    if requirements.max_gold is not None and state.gold > requirements.max_gold:
        missing.append(f"gold<={requirements.max_gold}")

    for item, count in requirements.owned_items:
        if owned_count(state, item) < count:
            missing.append(f"item:{item}>={count}")

    for flag in sorted(requirements.required_story_flags):
        if flag not in state.story_flags:
            missing.append(f"story_flag:{flag}")

    for flag in sorted(requirements.required_resource_flags):
        if flag not in state.resource_flags:
            missing.append(f"resource_flag:{flag}")

    for flag in sorted(requirements.forbidden_resource_flags):
        if flag in state.resource_flags:
            missing.append(f"forbidden_resource_flag:{flag}")

    for name in sorted(requirements.alive_members):
        try:
            member = state.member(name)
        except KeyError:
            missing.append(f"member:{name}")
            continue
        if not member.alive:
            missing.append(f"alive:{name}")

    return tuple(missing)


def is_feasible(state: DQ6State, requirements: ActionRequirements) -> bool:
    return not missing_requirements(state, requirements)


def _normalized_counts(values: dict[str, int]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted((name, count) for name, count in values.items() if count > 0))


def _replace_member(
    members: dict[str, PartyMemberState],
    name: str,
    member: PartyMemberState,
) -> None:
    if name not in members:
        raise KeyError(f"unknown party member: {name}")
    members[name] = member


def apply_resource_effect(state: DQ6State, effect: ResourceEffect) -> DQ6State:
    """確定的 resource effect を immutable な DQ6State へ適用する。"""

    gold = state.gold + effect.gold_delta
    if gold < 0:
        raise ValueError("resource effect would make gold negative")

    bag = dict(state.bag)
    for item, delta in effect.bag_deltas:
        bag[item] = bag.get(item, 0) + delta
        if bag[item] < 0:
            raise ValueError(f"resource effect would make bag item negative: {item}")

    members = {member.name: member for member in state.party}

    for name, item, delta in effect.personal_item_deltas:
        member = members.get(name)
        if member is None:
            raise KeyError(f"unknown party member: {name}")
        items = dict(member.personal_items)
        items[item] = items.get(item, 0) + delta
        if items[item] < 0:
            raise ValueError(
                f"resource effect would make personal item negative: {name}:{item}"
            )
        _replace_member(
            members,
            name,
            replace(member, personal_items=_normalized_counts(items)),
        )

    for name, stat, delta in effect.stat_deltas:
        member = members.get(name)
        if member is None:
            raise KeyError(f"unknown party member: {name}")
        stats = dict(member.stats)
        stats[stat] = stats.get(stat, 0) + delta
        _replace_member(
            members,
            name,
            replace(member, stats=_normalized_counts(stats)),
        )

    for change in effect.equipment_changes:
        member = members.get(change.member)
        if member is None:
            raise KeyError(f"unknown party member: {change.member}")
        equipment = dict(member.equipment)
        if change.item is None:
            equipment.pop(change.slot, None)
        else:
            equipment[change.slot] = change.item
        _replace_member(
            members,
            change.member,
            replace(member, equipment=tuple(sorted(equipment.items()))),
        )

    party = tuple(members[member.name] for member in state.party)
    resource_flags = (
        state.resource_flags - effect.remove_resource_flags
    ) | effect.add_resource_flags

    return replace(
        state,
        party=party,
        bag=_normalized_counts(bag),
        gold=gold,
        resource_flags=resource_flags,
    )
