from retro_opt.games.dq6.progression_registry import (
    audit_ram_semantic_gate_coverage,
    load_semantic_progression_gates,
    validate_semantic_progression_gates,
)


def test_semantic_progression_registry_references_known_chart_events() -> None:
    gates = load_semantic_progression_gates()
    assert gates
    assert validate_semantic_progression_gates(gates) == ()


def test_ram_and_semantic_registries_overlap_on_core_progression() -> None:
    audit = audit_ram_semantic_gate_coverage()

    for gate in (
        "dream_dew_obtained",
        "magic_key_obtained",
        "mermaid_harp_obtained",
        "hero_body_fused",
        "gracos_defeated",
        "hazama_access_unlocked",
        "normal_ending_complete",
    ):
        assert gate in audit.ram_and_semantic


def test_registry_audit_surfaces_reference_only_ram_flags() -> None:
    audit = audit_ram_semantic_gate_coverage()

    # These are useful observed RAM states but have not yet been promoted into
    # the high-level semantic progression registry.  Keep the gap explicit.
    assert "soldier_uniforms_obtained" in audit.ram_only
    assert "baptism_trial_1_defeated" in audit.ram_only


def test_semantic_only_gates_are_not_treated_as_ram_mapping_failures() -> None:
    audit = audit_ram_semantic_gate_coverage()

    # Some high-level gates are derived/composite concepts rather than a known
    # single RAM bit.  They should remain valid semantic gates.
    assert "four_legendary_equipment_gate_satisfied" in audit.semantic_only
