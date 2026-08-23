from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class UnknownReference:
    path: str
    value: str


def collect_unknown_references(value: Any, path: str = "$") -> list[UnknownReference]:
    """JSON-like object内の `unknown:` 参照を再帰的に列挙する。"""

    found: list[UnknownReference] = []

    if isinstance(value, str):
        if "unknown:" in value:
            found.append(UnknownReference(path=path, value=value))
        return found

    if isinstance(value, Mapping):
        for key, child in value.items():
            found.extend(collect_unknown_references(child, f"{path}.{key}"))
        return found

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            found.extend(collect_unknown_references(child, f"{path}[{index}]"))

    return found


def unresolved_parameter_values(value: Any) -> tuple[str, ...]:
    """重複を除いた unresolved 値を安定順序で返す。"""

    return tuple(
        sorted({reference.value for reference in collect_unknown_references(value)})
    )
