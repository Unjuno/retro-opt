from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Mapping, Sequence

from retro_opt.games.dq6.story_events import default_data_dir


RAM_FLAG_FILE = "ram_progression_flags_reference.json"
RAM_EVENT_REGION_START = 0x7E3D2A
RAM_EVENT_REGION_END = 0x7E3DFF


@dataclass(frozen=True, slots=True)
class RamProgressionFlag:
    address: int
    mask: int
    semantic_gate: str
    meaning_ja: str
    confidence: str
    note: str | None = None


@dataclass(frozen=True, slots=True)
class ProgressionFlagSnapshot:
    active_semantic_gates: frozenset[str]
    observed_addresses: frozenset[int]
    missing_addresses: frozenset[int]


def load_ram_progression_flags(
    data_dir: Path | str | None = None,
) -> tuple[RamProgressionFlag, ...]:
    base = Path(data_dir) if data_dir is not None else default_data_dir()
    payload = json.loads((base / RAM_FLAG_FILE).read_text(encoding="utf-8"))

    flags: list[RamProgressionFlag] = []
    for row in payload["flags"]:
        flags.append(
            RamProgressionFlag(
                address=int(str(row["address"]), 16),
                mask=int(str(row["mask"]), 16),
                semantic_gate=str(row["semantic_gate"]),
                meaning_ja=str(row["meaning_ja"]),
                confidence=str(row.get("confidence", "unknown")),
                note=str(row["note"]) if "note" in row else None,
            )
        )

    errors = validate_ram_progression_flags(flags)
    if errors:
        raise ValueError("invalid RAM progression flag reference: " + "; ".join(errors))
    return tuple(flags)


def validate_ram_progression_flags(
    flags: Sequence[RamProgressionFlag],
) -> tuple[str, ...]:
    errors: list[str] = []
    seen_bits: set[tuple[int, int]] = set()

    for flag in flags:
        if not RAM_EVENT_REGION_START <= flag.address <= RAM_EVENT_REGION_END:
            errors.append(f"address outside permanent event region: {flag.address:06X}")
        if flag.mask <= 0 or flag.mask > 0x80 or flag.mask & (flag.mask - 1):
            errors.append(
                f"mask must select exactly one bit: {flag.address:06X}:{flag.mask:02X}"
            )
        bit = (flag.address, flag.mask)
        if bit in seen_bits:
            errors.append(f"duplicate RAM flag bit: {flag.address:06X}:{flag.mask:02X}")
        seen_bits.add(bit)
        if not flag.semantic_gate:
            errors.append(f"empty semantic gate: {flag.address:06X}:{flag.mask:02X}")

    return tuple(errors)


def decode_progression_flags(
    memory: Mapping[int, int],
    flags: Sequence[RamProgressionFlag] | None = None,
) -> ProgressionFlagSnapshot:
    """Decode known semantic progression gates from an address->byte mapping.

    Missing RAM bytes are reported rather than silently treated as zero.  This
    matters when emulator integrations provide partial memory snapshots.
    """

    references = load_ram_progression_flags() if flags is None else tuple(flags)
    active: set[str] = set()
    observed: set[int] = set()
    missing: set[int] = set()

    for flag in references:
        if flag.address not in memory:
            missing.add(flag.address)
            continue
        value = int(memory[flag.address])
        if not 0 <= value <= 0xFF:
            raise ValueError(f"RAM byte out of range at {flag.address:06X}: {value}")
        observed.add(flag.address)
        if value & flag.mask:
            active.add(flag.semantic_gate)

    return ProgressionFlagSnapshot(
        active_semantic_gates=frozenset(active),
        observed_addresses=frozenset(observed),
        missing_addresses=frozenset(missing),
    )


def read_progression_flags(
    read_byte: Callable[[int], int],
    flags: Sequence[RamProgressionFlag] | None = None,
) -> ProgressionFlagSnapshot:
    """Read each referenced RAM byte once and decode its semantic gates."""

    references = load_ram_progression_flags() if flags is None else tuple(flags)
    addresses = sorted({flag.address for flag in references})
    memory = {address: read_byte(address) for address in addresses}
    return decode_progression_flags(memory, references)
