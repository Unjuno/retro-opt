from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PartyMemberState:
    """ROM addressに依存しないDQ6 party memberの抽象状態。"""

    name: str
    hp: int
    mp: int
    exp: int
    level: int
    alive: bool = True
    vocation: str | None = None
    proficiency: int | None = None
    equipment: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DQ6State:
    """solverが扱うDQ6の抽象状態。

    現段階ではRAM addressを一切含めない。後でGame Adapterがraw emulator state
    からこの構造へ変換する。
    """

    segment: str
    location: str
    party: tuple[PartyMemberState, ...]
    inventory: tuple[tuple[str, int], ...] = ()
    gold: int = 0
    story_flags: frozenset[str] = frozenset()
    encounter_count: int = 0
    observable_tags: frozenset[str] = frozenset()

    def member(self, name: str) -> PartyMemberState:
        for member in self.party:
            if member.name == name:
                return member
        raise KeyError(name)
