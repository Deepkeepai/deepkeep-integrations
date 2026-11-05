from dataclasses import dataclass, field
from typing import Any

import pytest

from strands_deepkeep.guardrail import (
    DeepKeepGuardrail,
    _highest_priority_action,
    _modified_content,
)


class FakeClient:
    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        self.calls: list[dict[str, Any]] = []

    def pre_moderate(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return self.result

    def post_moderate(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return self.result


@dataclass
class FakeBeforeInvocationEvent:
    messages: list[dict[str, Any]]
    invocation_state: dict[str, Any] = field(default_factory=dict)
    cancel: bool | str = False


@dataclass
class FakeStopResponse:
    message: dict[str, Any]
    stop_reason: str = "end_turn"


@dataclass
class FakeAfterModelCallEvent:
    stop_response: FakeStopResponse
    invocation_state: dict[str, Any] = field(default_factory=dict)


def test_highest_priority_action_prefers_block():
    result = {
        "verbosity": [
            {"details": {"guardrail_action": "alert"}},
            {"details": {"guardrail_action": "modify"}},
            {"details": {"guardrail_action": "block"}},
        ]
    }

    assert _highest_priority_action(result) == "block"


def test_modified_content_uses_latest_modified_item():
    result = {
        "verbosity": [
            {"details": {"modified": [{"content": "first"}]}},
            {"details": {"modified": [{"content": "second"}]}},
        ]
    }

    assert _modified_content(result) == "second"


def test_guardrail_requires_at_least_one_model():
    with pytest.raises(ValueError):
        DeepKeepGuardrail(api_key="dk-test", base_url="https://deepkeep.example")


def test_before_invocation_replaces_redacted_user_text():
    guardrail = DeepKeepGuardrail(api_key="dk-test", base_url="https://deepkeep.example", pre_model="fw-input")
    result = {"verbosity": [{"details": {"guardrail_action": "redact", "modified": [{"content": "safe"}]}}]}
    guardrail.client = FakeClient(result)
    event = FakeBeforeInvocationEvent(messages=[{"role": "user", "content": [{"text": "secret"}]}])

    guardrail.before_invocation(event)

    assert event.messages[0]["content"][0]["text"] == "safe"
    assert event.cancel is False
    assert event.invocation_state["deepkeep_pre"] == result


def test_before_invocation_cancels_on_block():
    guardrail = DeepKeepGuardrail(api_key="dk-test", base_url="https://deepkeep.example", pre_model="fw-input")
    result = {"verbosity": [{"details": {"guardrail_action": "block"}}]}
    guardrail.client = FakeClient(result)
    event = FakeBeforeInvocationEvent(messages=[{"role": "user", "content": [{"text": "bad"}]}])

    guardrail.before_invocation(event)

    assert event.cancel == "DeepKeep blocked this content."


def test_after_model_call_replaces_redacted_output():
    guardrail = DeepKeepGuardrail(api_key="dk-test", base_url="https://deepkeep.example", post_model="fw-output")
    result = {"verbosity": [{"details": {"guardrail_action": "modify", "modified": [{"content": "safe output"}]}}]}
    guardrail.client = FakeClient(result)
    message = {"role": "assistant", "content": [{"text": "raw output"}]}
    event = FakeAfterModelCallEvent(stop_response=FakeStopResponse(message=message))

    guardrail.after_model_call(event)

    assert message["content"][0]["text"] == "safe output"
    assert message["metadata"]["custom"]["deepkeep"] == result
    assert event.invocation_state["deepkeep_post"] == result


def test_after_model_call_clears_blocked_output():
    guardrail = DeepKeepGuardrail(api_key="dk-test", base_url="https://deepkeep.example", post_model="fw-output")
    result = {"verbosity": [{"details": {"guardrail_action": "block"}}]}
    guardrail.client = FakeClient(result)
    message = {"role": "assistant", "content": [{"text": "unsafe output"}]}
    event = FakeAfterModelCallEvent(stop_response=FakeStopResponse(message=message))

    guardrail.after_model_call(event)

    assert message["content"][0]["text"] == ""
    assert message["metadata"]["custom"]["deepkeep"] == result
