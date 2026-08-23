from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from retro_opt.games.dq6.graph_codec import (
    decode_deterministic_effects,
    decode_requirements,
)


@dataclass(frozen=True, slots=True)
class CodecIssue:
    node_id: str
    action_id: str
    field: str
    detail: str


def audit_graph_codec(graph: Mapping[str, Any]) -> tuple[CodecIssue, ...]:
    """DQ6 graph actionが現在のtyped codecで解釈可能かを監査する。"""

    issues: list[CodecIssue] = []

    for node in graph.get("nodes", []):
        node_id = str(node.get("id", "<unknown>"))
        for action in node.get("actions", []) or []:
            action_id = str(action.get("id", "<unknown>"))

            try:
                decode_requirements(action.get("requirements"))
            except (TypeError, ValueError) as exc:
                issues.append(
                    CodecIssue(node_id, action_id, "requirements", str(exc))
                )

            effects = action.get("deterministic_effects")
            try:
                decoded = decode_deterministic_effects(effects)
            except (TypeError, ValueError) as exc:
                issues.append(
                    CodecIssue(node_id, action_id, "deterministic_effects", str(exc))
                )
            else:
                for unresolved in decoded.unresolved:
                    issues.append(
                        CodecIssue(
                            node_id,
                            action_id,
                            "deterministic_effects",
                            f"{unresolved.token}: {unresolved.reason}",
                        )
                    )

    return tuple(issues)
