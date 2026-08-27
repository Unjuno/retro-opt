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
    events / resource placement / cumulative counters が数イベント先の可否・戦闘時間・
    勝率・金策を変えるため、それらを state の一級要素として保持する。

    `completed_chart_events` は公開SFCフラグチャートの参照IDであり、RAM bit IDではない。
    `story_flags` は人間可読なsemantic event flagを保持する。RAM mappingは別レイヤで扱う。
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

    # ゲーム意味上の不可逆な進行。実RAMのbit番号とは独立した名前を使う。
    story_flags: frozenset[str] = frozenset()
    resource_flags: frozenset[str] = frozenset()

    # 公開フラグチャート 1..225 の完了状態。RAM event flag IDではない。
    completed_chart_events: frozenset[int] = frozenset()

    # Booleanで表現できないイベント進行。
    # 例: moon_mirror_orbs_destroyed=0..4, raidock_memory_points=0..6
    event_counters: tuple[tuple[str, int], ...] = ()
    # 例: hols_escort_stage, rob_follow_stage, prison_town_stage
    event_stages: tuple[tuple[str, str], ...] = ()

    # mapを跨がず消える/一時的にlegal actionを変えるイベント状態。
    temporary_event_flags: frozenset[str] = frozenset()
    # 関所・船・水門・飛行手段・世界復活など地理的到達可能性を変える状態。
    world_unlocks: frozenset[str] = frozenset()

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

    def event_counter(self, name: str, default: int = 0) -> int:
        return dict(self.event_counters).get(name, default)

    def event_stage(self, name: str, default: str | None = None) -> str | None:
        return dict(self.event_stages).get(name, default)

    def chart_event_completed(self, event_id: int) -> bool:
        return event_id in self.completed_chart_events

    def owns(self, item: str) -> bool:
        if self.bag_count(item) > 0:
            return True
        for member in self.party:
            if dict(member.personal_items).get(item, 0) > 0:
                return True
            if item in dict(member.equipment).values():
                return True
        return False
