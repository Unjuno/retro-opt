from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PartyMemberState:
    """ROM addressに依存しないDQ6 party memberの抽象状態。

    `stats` は RAM layout が確定するまで名前付き値として保持する。
    種・装備・level差が下流戦闘へ与える影響を state として失わないための項目。
    """

    name: str
    hp: int
    mp: int
    exp: int
    level: int
    alive: bool = True
    vocation: str | None = None
    proficiency: int | None = None
    stats: tuple[tuple[str, int], ...] = ()
    equipment: tuple[tuple[str, str], ...] = ()
    personal_items: tuple[tuple[str, int], ...] = ()
    status: frozenset[str] = frozenset()

    def stat(self, name: str, default: int | None = None) -> int | None:
        return dict(self.stats).get(name, default)

    def equipped(self, slot: str) -> str | None:
        return dict(self.equipment).get(slot)


@dataclass(frozen=True, slots=True)
class DQ6State:
    """solverが扱うDQ6の抽象状態。

    現段階ではRAM addressを一切含めない。後でGame Adapterがraw emulator state
    からこの構造へ変換する。

    DQ6のroute optimizationでは、EXPだけでなく item / equipment / gold / stats /
    flags / resource placement / cumulative counters が数イベント先の可否・戦闘時間・
    勝率・金策を変えるため、それらを state の一級要素として保持する。
    """

    segment: str
    location: str
    party: tuple[PartyMemberState, ...]

    # 袋。各キャラの手持ちは PartyMemberState.personal_items で分離する。
    bag: tuple[tuple[str, int], ...] = ()
    gold: int = 0

    # 小さなメダル累積、カジノコイン、永続的な戦闘/熟練度count等、
    # item所持とは別に将来条件を変える数値を保持する。
    counters: tuple[tuple[str, int], ...] = ()

    # 回収済み/売却済み/消費済み等を含む不可逆な進行はflagで保持する。
    story_flags: frozenset[str] = frozenset()
    resource_flags: frozenset[str] = frozenset()

    encounter_count: int = 0
    observable_tags: frozenset[str] = frozenset()

    def member(self, name: str) -> PartyMemberState:
        for member in self.party:
            if member.name == name:
                return member
        raise KeyError(name)

    def bag_count(self, item: str) -> int:
        return dict(self.bag).get(item, 0)

    def counter(self, name: str, default: int = 0) -> int:
        return dict(self.counters).get(name, default)

    def owns(self, item: str) -> bool:
        if self.bag_count(item) > 0:
            return True
        for member in self.party:
            if dict(member.personal_items).get(item, 0) > 0:
                return True
            if item in dict(member.equipment).values():
                return True
        return False
