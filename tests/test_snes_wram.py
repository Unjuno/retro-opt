import pytest

from retro_opt.emulator.snes import (
    SNES_WRAM_CPU_END,
    SNES_WRAM_CPU_START,
    SNES_WRAM_SIZE,
    snes_wram_cpu_address,
    snes_wram_offset,
)


def test_direct_wram_cpu_address_to_domain_offset() -> None:
    assert snes_wram_offset(0x7E0000) == 0x00000
    assert snes_wram_offset(0x7E3D2A) == 0x03D2A
    assert snes_wram_offset(0x7F0000) == 0x10000
    assert snes_wram_offset(0x7FFFFF) == 0x1FFFF


def test_wram_domain_offset_round_trip() -> None:
    for offset in (0, 0x3D2A, 0x10000, SNES_WRAM_SIZE - 1):
        assert snes_wram_offset(snes_wram_cpu_address(offset)) == offset


def test_non_direct_wram_cpu_address_is_rejected() -> None:
    with pytest.raises(ValueError):
        snes_wram_offset(SNES_WRAM_CPU_START - 1)
    with pytest.raises(ValueError):
        snes_wram_offset(SNES_WRAM_CPU_END + 1)


def test_invalid_wram_offset_is_rejected() -> None:
    with pytest.raises(ValueError):
        snes_wram_cpu_address(-1)
    with pytest.raises(ValueError):
        snes_wram_cpu_address(SNES_WRAM_SIZE)
