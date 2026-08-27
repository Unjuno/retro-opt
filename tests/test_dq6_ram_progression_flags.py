import json

from retro_opt.games.dq6.story_events import default_data_dir


def _payload() -> dict:
    return json.loads(
        (default_data_dir() / "ram_progression_flags_reference.json").read_text(
            encoding="utf-8"
        )
    )


def test_ram_flag_address_mask_pairs_are_unique() -> None:
    payload = _payload()
    pairs = [(row["address"], row["mask"]) for row in payload["flags"]]
    assert len(pairs) == len(set(pairs))


def test_known_progression_flag_mappings() -> None:
    payload = _payload()
    flags = {row["semantic_gate"]: (row["address"], row["mask"]) for row in payload["flags"]}

    assert flags["dream_dew_obtained"] == ("7E3D35", "20")
    assert flags["mirror_key_obtained"] == ("7E3D35", "40")
    assert flags["ra_mirror_obtained"] == ("7E3D35", "80")
    assert flags["mermaid_harp_obtained"] == ("7E3D36", "20")
    assert flags["orgo_armor_obtained"] == ("7E3D37", "04")
    assert flags["real_mudo_defeated"] == ("7E3D60", "01")
    assert flags["magic_key_obtained"] == ("7E3D6C", "10")
    assert flags["hazama_access_unlocked"] == ("7E3D71", "20")
    assert flags["normal_ending_complete"] == ("7E3D6C", "40")


def test_non_bit_progression_state_is_kept_separate() -> None:
    payload = _payload()
    rows = {row["address"]: row["model_field"] for row in payload["non_bit_event_state"]}

    assert rows["7E3D29"].startswith("event_counter_or_stage")
    assert rows["7E3E08"].startswith("event_counter")
