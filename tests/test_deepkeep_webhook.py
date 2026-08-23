from __future__ import annotations

import os

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

os.environ.setdefault("DEEPKEEP_BASE_URL", "https://deepkeep.example")
os.environ.setdefault("DEEPKEEP_API_KEY", "dk-test")
os.environ.setdefault("DEEPKEEP_MODEL", "fw-test")

from deepkeep_webhook import DeepKeepClient, DeepKeepConfig, create_app


def make_client() -> TestClient:
    config = DeepKeepConfig(
        base_url="https://deepkeep.example",
        api_key="dk-test",
        model="fw-test",
        title="agentgateway",
        chat="chat-1",
    )
    return TestClient(create_app(DeepKeepClient(config)))


def prompt_body(text: str = "hello") -> dict:
    return {"body": {"messages": [{"role": "user", "content": text}]}}


def response_body(text: str = "hello") -> dict:
    return {"body": {"choices": [{"message": {"role": "assistant", "content": text}}]}}


def moderation_result(action: str | None = None, *, modified: str | None = None) -> dict:
    if action is None:
        return {"flagged": False, "verbosity": []}
    details = {"guardrail_action": action, "message": f"{action} reason"}
    if modified is not None:
        details["modified"] = [{"content": modified}]
    return {"flagged": True, "verbosity": [{"name": "guardrail", "details": details}]}


@respx.mock
def test_request_posts_to_deepkeep_pre_endpoint():
    route = respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json=moderation_result())
    )

    response = make_client().post("/request", json=prompt_body("hello"))

    assert response.status_code == 200
    assert route.calls.last.request.headers["X-API-Key"] == "dk-test"
    assert route.calls.last.request.content == b'{"model":"fw-test","input":"hello","title":"agentgateway","chat":"chat-1"}'


@respx.mock
def test_response_posts_to_deepkeep_post_endpoint():
    route = respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json=moderation_result())
    )

    response = make_client().post("/response", json=response_body("hello"))

    assert response.status_code == 200
    assert route.calls.last.request.content == b'{"model":"fw-test","output":"hello","title":"agentgateway","chat":"chat-1"}'


@respx.mock
def test_request_passes_when_deepkeep_has_no_action():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json=moderation_result())
    )

    response = make_client().post("/request", json=prompt_body())

    assert response.json() == {"action": {"reason": "DeepKeep allowed this content."}}


@respx.mock
def test_request_rejects_on_block():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json=moderation_result("block"))
    )

    response = make_client().post("/request", json=prompt_body())

    assert response.json() == {
        "action": {"body": "block reason", "status_code": 403, "reason": "block reason"}
    }


@respx.mock
@pytest.mark.parametrize("action", ["redact", "modify"])
def test_request_masks_on_modified_content(action):
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json=moderation_result(action, modified="safe prompt"))
    )

    response = make_client().post("/request", json=prompt_body("unsafe prompt"))

    assert response.json()["action"]["body"] == {"messages": [{"role": "user", "content": "safe prompt"}]}


@respx.mock
def test_request_rejects_unknown_action():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json=moderation_result("quarantine"))
    )

    response = make_client().post("/request", json=prompt_body())

    assert response.json() == {
        "action": {
            "body": "DeepKeep returned unsupported guardrail action: quarantine",
            "status_code": 403,
            "reason": "DeepKeep returned unsupported guardrail action: quarantine",
        }
    }


@respx.mock
def test_response_passes_when_deepkeep_has_no_action():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json=moderation_result())
    )

    response = make_client().post("/response", json=response_body())

    assert response.json() == {"action": {"reason": "DeepKeep allowed this content."}}


@respx.mock
@pytest.mark.parametrize("action", ["redact", "modify"])
def test_response_masks_on_modified_content(action):
    respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json=moderation_result(action, modified="safe response"))
    )

    response = make_client().post("/response", json=response_body("unsafe response"))

    assert response.json()["action"]["body"] == {
        "choices": [{"message": {"role": "assistant", "content": "safe response"}}]
    }


@respx.mock
def test_response_clears_content_on_block():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json=moderation_result("block"))
    )

    response = make_client().post("/response", json=response_body("unsafe response"))

    assert response.json()["action"] == {
        "body": {"choices": [{"message": {"role": "assistant", "content": ""}}]},
        "reason": "block reason",
    }


@respx.mock
def test_response_clears_content_on_unknown_action():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json=moderation_result("quarantine"))
    )

    response = make_client().post("/response", json=response_body("unsafe response"))

    assert response.json()["action"] == {
        "body": {"choices": [{"message": {"role": "assistant", "content": ""}}]},
        "reason": "DeepKeep returned unsupported guardrail action: quarantine",
    }


@respx.mock
def test_deepkeep_error_returns_bad_gateway():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(500, text="boom")
    )

    response = make_client().post("/request", json=prompt_body())

    assert response.status_code == 502
    assert "DeepKeep API error 500" in response.json()["detail"]
