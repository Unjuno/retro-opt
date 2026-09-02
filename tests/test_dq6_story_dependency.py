from retro_opt.games.dq6.story_dependency import (
    dependency_evidence_for_subject,
    hard_dependency_evidence,
    load_story_dependency_evidence,
    uncertain_dependency_evidence,
)


def test_dependency_evidence_ids_are_unique_and_sourced() -> None:
    rows = load_story_dependency_evidence()
    assert rows
    assert len({row.id for row in rows}) == len(rows)
    assert all(row.sources for row in rows)


def test_knowledge_only_relations_are_not_returned_as_hard_constraints() -> None:
    hard_ids = {row.id for row in hard_dependency_evidence()}
    assert "grace_ritual_is_knowledge_only" not in hard_ids
    assert "mysterious_cave_hints_are_knowledge_only" not in hard_ids
    assert "secret_lake_information_is_optional" not in hard_ids


def test_verified_hard_relations_are_enforceable() -> None:
    hard_ids = {row.id for row in hard_dependency_evidence()}
    assert "river_passage_discovery" in hard_ids
    assert "ice_cave_zam_flag" in hard_ids
    assert "magician_tower_inpas" in hard_ids
    assert "legendary_equipment_join" in hard_ids
    assert "tenma_last_key_join" in hard_ids


def test_hazama_order_discrepancy_remains_explicitly_uncertain() -> None:
    uncertain_ids = {row.id for row in uncertain_dependency_evidence()}
    assert "hazama_restore_vs_lake_order" in uncertain_ids


def test_subject_lookup_keeps_set_gate_semantics() -> None:
    rows = dependency_evidence_for_subject("chart_event:52")
    assert len(rows) == 1
    assert rows[0].kind == "unordered_set_gate"
    assert rows[0].optimizer_action == "model_as_set_not_sequence"
