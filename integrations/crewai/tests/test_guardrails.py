from crewai_deepkeep.guardrails import DeepKeepGuardrail


class FakeClient:
    def __init__(self, decision):
        self.decision = decision

    def post_decision(self, **kwargs):
        return self.decision


class Output:
    raw = "hello"


def guardrail_with(decision):
    guardrail = DeepKeepGuardrail(api_key="key", base_url="https://deepkeep.test", post_model="model")
    guardrail.client = FakeClient(decision)
    return guardrail


def test_guardrail_returns_original_when_allowed() -> None:
    from crewai_deepkeep.client import DeepKeepDecision

    output = Output()
    result = guardrail_with(DeepKeepDecision()).check_output(output)

    assert result == (True, output)


def test_guardrail_returns_feedback_when_blocked() -> None:
    from crewai_deepkeep.client import DeepKeepDecision

    result = guardrail_with(DeepKeepDecision(action="block", reason="blocked")).check_output(Output())

    assert result == (False, "blocked")


def test_guardrail_returns_modified_content() -> None:
    from crewai_deepkeep.client import DeepKeepDecision

    result = guardrail_with(
        DeepKeepDecision(action="redact", modified_content="safe")
    ).check_output(Output())

    assert result == (True, "safe")
