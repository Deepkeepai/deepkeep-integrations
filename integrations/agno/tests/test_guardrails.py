import pytest

from agno.exceptions import InputCheckError, OutputCheckError
from agno.run.agent import RunInput, RunOutput

from agno_deepkeep import DeepKeepDecision, DeepKeepGuardrail


class FakeClient:
    def __init__(self, decision):
        self.decision = decision

    def pre_decision(self, **kwargs):
        self.kwargs = kwargs
        return self.decision

    def post_decision(self, **kwargs):
        self.kwargs = kwargs
        return self.decision


def guardrail_with(decision, *, pre_model="input-firewall", post_model="output-firewall"):
    guardrail = DeepKeepGuardrail(
        api_key="dk-test",
        base_url="https://deepkeep.example",
        pre_model=pre_model,
        post_model=post_model,
    )
    guardrail.client = FakeClient(decision)
    return guardrail


def test_check_allows_input():
    guardrail = guardrail_with(DeepKeepDecision())
    run_input = RunInput(input_content="hello")

    guardrail.check(run_input=run_input)

    assert run_input.input_content == "hello"
    assert guardrail.client.kwargs["model"] == "input-firewall"
    assert guardrail.client.kwargs["input"] == "hello"


def test_check_blocks_input():
    guardrail = guardrail_with(DeepKeepDecision(action="block", reason="blocked"))

    with pytest.raises(InputCheckError) as exc_info:
        guardrail.check(run_input=RunInput(input_content="bad"))

    assert "blocked" in str(exc_info.value)


def test_check_replaces_input_for_redact_or_modify():
    guardrail = guardrail_with(DeepKeepDecision(action="redact", modified_content="safe"))
    run_input = RunInput(input_content="secret")

    guardrail.check(run_input=run_input)

    assert run_input.input_content == "safe"


def test_check_output_posts_and_replaces_content():
    guardrail = guardrail_with(DeepKeepDecision(action="modify", modified_content="safe output"))
    run_output = RunOutput(content="unsafe output")

    guardrail.check(run_output=run_output)

    assert run_output.content == "safe output"
    assert guardrail.client.kwargs["model"] == "output-firewall"
    assert guardrail.client.kwargs["output"] == "unsafe output"


def test_check_output_blocks():
    guardrail = guardrail_with(DeepKeepDecision(action="block", reason="blocked"))

    with pytest.raises(OutputCheckError) as exc_info:
        guardrail.check(run_output=RunOutput(content="bad output"))

    assert "blocked" in str(exc_info.value)


def test_unsupported_action_fails_closed():
    guardrail = guardrail_with(DeepKeepDecision(unsupported_action="quarantine"))

    with pytest.raises(InputCheckError) as exc_info:
        guardrail.check(run_input=RunInput(input_content="hello"))

    assert "quarantine" in str(exc_info.value)
