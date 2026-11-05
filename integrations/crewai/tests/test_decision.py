from crewai_deepkeep.client import decision_from_response


def test_decision_allows_empty_response() -> None:
    decision = decision_from_response({"verbosity": []})

    assert decision.allowed
    assert decision.action is None


def test_decision_blocks_highest_priority_action() -> None:
    decision = decision_from_response(
        {
            "verbosity": [
                {"details": {"guardrail_action": "alert", "message": "low"}},
                {"details": {"guardrail_action": "block", "message": "blocked"}},
            ]
        }
    )

    assert not decision.allowed
    assert decision.action == "block"
    assert decision.reason == "blocked"


def test_decision_extracts_modified_content() -> None:
    decision = decision_from_response(
        {
            "verbosity": [
                {
                    "details": {
                        "guardrail_action": "redact",
                        "modified": [{"content": "safe text"}],
                    }
                }
            ]
        }
    )

    assert decision.should_replace
    assert decision.modified_content == "safe text"
