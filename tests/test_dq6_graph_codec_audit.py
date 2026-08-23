from retro_opt.games.dq6.graph_codec_audit import audit_graph_codec


def test_codec_audit_reports_unknown_requirements_and_untyped_effects() -> None:
    graph = {
        "nodes": [
            {
                "id": "shop",
                "actions": [
                    {
                        "id": "sell",
                        "requirements": {"owned_sellable_asset": True},
                        "deterministic_effects": ["gold:+unknown:sale_value"],
                    },
                    {
                        "id": "buy",
                        "requirements": {"min_gold": 720},
                        "deterministic_effects": [
                            "gold:-720",
                            "bag:iron_shield:+1",
                        ],
                    },
                ],
            }
        ]
    }

    issues = audit_graph_codec(graph)
    assert [(issue.action_id, issue.field) for issue in issues] == [
        ("sell", "requirements"),
        ("sell", "deterministic_effects"),
    ]


def test_codec_audit_accepts_typed_action() -> None:
    graph = {
        "nodes": [
            {
                "id": "chest",
                "actions": [
                    {
                        "id": "take",
                        "requirements": {"max_gold": 140},
                        "deterministic_effects": [
                            "gold:+200",
                            "counter:small_medals:+1",
                            "mark:collected",
                        ],
                    }
                ],
            }
        ]
    }
    assert audit_graph_codec(graph) == ()
