from retro_opt.games.dq6.ram_progression import (
    RamProgressionFlag,
    decode_progression_flags,
    load_ram_progression_flags,
    read_progression_flags,
    validate_ram_progression_flags,
)


def test_public_ram_progression_reference_is_structurally_valid() -> None:
    flags = load_ram_progression_flags()
    assert flags
    assert validate_ram_progression_flags(flags) == ()


def test_decode_known_progression_bits() -> None:
    flags = load_ram_progression_flags()
    memory = {
        0x7E3D35: 0x20 | 0x80,  # Dream Dew + Ra's Mirror
        0x7E3D36: 0x20,         # Mermaid Harp
        0x7E3D6C: 0x10,         # Magic Key
    }

    snapshot = decode_progression_flags(memory, flags)

    assert "dream_dew_obtained" in snapshot.active_semantic_gates
    assert "ra_mirror_obtained" in snapshot.active_semantic_gates
    assert "mermaid_harp_obtained" in snapshot.active_semantic_gates
    assert "magic_key_obtained" in snapshot.active_semantic_gates
    assert "mirror_key_obtained" not in snapshot.active_semantic_gates
    assert 0x7E3D35 in snapshot.observed_addresses
    assert snapshot.missing_addresses


def test_reader_reads_each_referenced_address_once() -> None:
    flags = (
        RamProgressionFlag(0x7E3D35, 0x20, "a", "A", "high"),
        RamProgressionFlag(0x7E3D35, 0x40, "b", "B", "high"),
        RamProgressionFlag(0x7E3D36, 0x01, "c", "C", "high"),
    )
    calls: list[int] = []

    def read_byte(address: int) -> int:
        calls.append(address)
        return {0x7E3D35: 0x60, 0x7E3D36: 0x00}[address]

    snapshot = read_progression_flags(read_byte, flags)

    assert calls == [0x7E3D35, 0x7E3D36]
    assert snapshot.active_semantic_gates == frozenset({"a", "b"})
    assert not snapshot.missing_addresses


def test_invalid_reference_mask_is_rejected() -> None:
    flags = (RamProgressionFlag(0x7E3D35, 0x03, "bad", "bad", "low"),)
    errors = validate_ram_progression_flags(flags)
    assert errors
    assert "mask must select exactly one bit" in errors[0]


def test_decode_rejects_non_byte_values() -> None:
    flags = (RamProgressionFlag(0x7E3D35, 0x20, "a", "A", "high"),)

    try:
        decode_progression_flags({0x7E3D35: 256}, flags)
    except ValueError as exc:
        assert "RAM byte out of range" in str(exc)
    else:
        raise AssertionError("expected ValueError")
