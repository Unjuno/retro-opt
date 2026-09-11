from __future__ import annotations


SNES_WRAM_CPU_START = 0x7E0000
SNES_WRAM_CPU_END = 0x7FFFFF
SNES_WRAM_SIZE = 0x20000


def snes_wram_offset(cpu_address: int) -> int:
    """Convert a direct SNES CPU WRAM address to a WRAM-domain offset.

    Direct WRAM occupies CPU addresses $7E0000-$7FFFFF.  Emulator APIs that
    expose WRAM as its own 128 KiB memory domain normally address that domain
    from zero, so $7E3D2A becomes offset $3D2A and $7F0000 becomes $10000.

    This helper deliberately rejects mirrored low-bank WRAM addresses such as
    $00:0000-$1FFF; callers must normalize those separately if needed.
    """

    if not isinstance(cpu_address, int):
        raise TypeError("cpu_address must be an int")
    if not SNES_WRAM_CPU_START <= cpu_address <= SNES_WRAM_CPU_END:
        raise ValueError(
            "address is outside direct SNES WRAM mapping "
            f"$7E0000-$7FFFFF: ${cpu_address:06X}"
        )
    return cpu_address - SNES_WRAM_CPU_START


def snes_wram_cpu_address(offset: int) -> int:
    """Convert a WRAM-domain offset back to its direct SNES CPU address."""

    if not isinstance(offset, int):
        raise TypeError("offset must be an int")
    if not 0 <= offset < SNES_WRAM_SIZE:
        raise ValueError(f"WRAM offset out of range: 0x{offset:X}")
    return SNES_WRAM_CPU_START + offset
