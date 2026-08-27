from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping, Sequence

from retro_opt.games.dq6.ram_progression import RamProgressionFlag, load_ram_progression_flags
from retro_opt.games.dq6.story_events import StoryEvent, default_data_dir, load_story_events


SEMANTIC_GATE_FILE = "story_progression_gates.json"


@dataclass(frozen=True, slots=True)
class SemanticProgressionGate:
    id: str
    kind: str
    after: tuple[int, ...]
    confidence: str
    raw: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ProgressionRegistryAudit:
    ram_and_semantic: frozenset[str]
    ram_only: frozenset[str]
    semantic_only: frozenset[str]


def default_model_dir() -> Path:
    return default_data_dir().parent / "model"


def load_semantic_progression_gates(
    model_dir: Path | str | None = None,
) -> dict[str, SemanticProgressionGate]:
    base = Path(model_dir) if model_dir is not None else default_model_dir()
    payload = json.loads((base / SEMANTIC_GATE_FILE).read_text(encoding="utf-8"))

    gates: dict[str, SemanticProgressionGate] = {}
    for row in payload["gates"]:
        gate_id = str(row["id"])
        if gate_id in gates:
            raise ValueError(f"duplicate semantic progression gate: {gate_id}")
        gates[gate_id] = SemanticProgressionGate(
            id=gate_id,
            kind=str(row["kind"]),
            after=tuple(int(value) for value in row.get("after", ())),
            confidence=str(row.get("confidence", "unknown")),
            raw=row,
        )

    return gates


def validate_semantic_progression_gates(
    gates: Mapping[str, SemanticProgressionGate],
    events: Mapping[int, StoryEvent] | None = None,
) -> tuple[str, ...]:
    event_map = load_story_events() if events is None else events
    errors: list[str] = []

    for gate_id, gate in sorted(gates.items()):
        if not gate_id:
            errors.append("empty semantic gate id")
        if not gate.after:
            errors.append(f"semantic gate has no chart evidence: {gate_id}")
        for event_id in gate.after:
            if event_id not in event_map:
                errors.append(f"semantic gate {gate_id} references unknown event {event_id}")

    return tuple(errors)


def audit_ram_semantic_gate_coverage(
    ram_flags: Sequence[RamProgressionFlag] | None = None,
    semantic_gates: Mapping[str, SemanticProgressionGate] | None = None,
) -> ProgressionRegistryAudit:
    references = load_ram_progression_flags() if ram_flags is None else tuple(ram_flags)
    gates = load_semantic_progression_gates() if semantic_gates is None else semantic_gates

    ram_names = frozenset(flag.semantic_gate for flag in references)
    semantic_names = frozenset(gates)

    return ProgressionRegistryAudit(
        ram_and_semantic=ram_names & semantic_names,
        ram_only=ram_names - semantic_names,
        semantic_only=semantic_names - ram_names,
    )
