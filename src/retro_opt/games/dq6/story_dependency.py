from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class StoryDependencyEvidence:
    id: str
    subject: str
    dependency: str
    kind: str
    optimizer_action: str
    confidence: str
    note: str
    sources: tuple[str, ...]


def default_dependency_evidence_path() -> Path:
    return (
        Path(__file__).resolve().parents[4]
        / "games"
        / "sfc"
        / "dq6"
        / "model"
        / "story_dependency_evidence.json"
    )


def load_story_dependency_evidence(
    path: Path | str | None = None,
) -> tuple[StoryDependencyEvidence, ...]:
    source = Path(path) if path is not None else default_dependency_evidence_path()
    payload = json.loads(source.read_text(encoding="utf-8"))

    result: list[StoryDependencyEvidence] = []
    seen: set[str] = set()
    for row in payload["relations"]:
        relation_id = str(row["id"])
        if relation_id in seen:
            raise ValueError(f"duplicate dependency evidence id: {relation_id}")
        seen.add(relation_id)
        result.append(
            StoryDependencyEvidence(
                id=relation_id,
                subject=str(row["subject"]),
                dependency=str(row["dependency"]),
                kind=str(row["kind"]),
                optimizer_action=str(row["optimizer_action"]),
                confidence=str(row["confidence"]),
                note=str(row.get("note", "")),
                sources=tuple(str(value) for value in row.get("sources", ())),
            )
        )
    return tuple(result)


def dependency_evidence_for_subject(
    subject: str,
    evidence: Iterable[StoryDependencyEvidence] | None = None,
) -> tuple[StoryDependencyEvidence, ...]:
    rows = load_story_dependency_evidence() if evidence is None else tuple(evidence)
    return tuple(row for row in rows if row.subject == subject)


def uncertain_dependency_evidence(
    evidence: Iterable[StoryDependencyEvidence] | None = None,
) -> tuple[StoryDependencyEvidence, ...]:
    rows = load_story_dependency_evidence() if evidence is None else tuple(evidence)
    return tuple(
        row
        for row in rows
        if row.kind.startswith("uncertain") or row.optimizer_action == "verify_before_prune_or_exploit"
    )


def hard_dependency_evidence(
    evidence: Iterable[StoryDependencyEvidence] | None = None,
) -> tuple[StoryDependencyEvidence, ...]:
    """Return relations currently safe to enforce as optimizer constraints.

    Knowledge-only and unresolved relations are intentionally excluded.  The
    raw 1..225 chart graph remains a separate provenance layer; this function
    only exposes relations for which the research layer says enforcement is
    appropriate.
    """

    rows = load_story_dependency_evidence() if evidence is None else tuple(evidence)
    enforce_actions = {
        "enforce",
        "enforce_separately_from_chart_dependencies",
        "enforce_equipment_but_treat_symbol_discovery_as_knowledge_only",
    }
    return tuple(row for row in rows if row.optimizer_action in enforce_actions)
