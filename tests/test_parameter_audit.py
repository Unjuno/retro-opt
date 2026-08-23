from retro_opt.analysis.parameter_audit import (
    collect_unknown_references,
    unresolved_parameter_values,
)


def test_collect_unknown_references_tracks_paths() -> None:
    value = {
        "duration_model": "unknown:walk-time",
        "actions": [
            {"effect": "gold:+unknown:sale_value"},
            {"effect": "known"},
        ],
    }

    refs = collect_unknown_references(value)
    assert [(ref.path, ref.value) for ref in refs] == [
        ("$.duration_model", "unknown:walk-time"),
        ("$.actions[0].effect", "gold:+unknown:sale_value"),
    ]


def test_unresolved_parameter_values_are_unique_and_sorted() -> None:
    value = [
        "unknown:b",
        {"x": "unknown:a"},
        "unknown:b",
    ]
    assert unresolved_parameter_values(value) == ("unknown:a", "unknown:b")
