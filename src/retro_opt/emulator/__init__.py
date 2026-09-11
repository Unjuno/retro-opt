"""Emulator-independent address and readout helpers."""

from retro_opt.emulator.snes import (
    SNES_WRAM_CPU_END,
    SNES_WRAM_CPU_START,
    SNES_WRAM_SIZE,
    snes_wram_cpu_address,
    snes_wram_offset,
)

__all__ = [
    "SNES_WRAM_CPU_END",
    "SNES_WRAM_CPU_START",
    "SNES_WRAM_SIZE",
    "snes_wram_cpu_address",
    "snes_wram_offset",
]
