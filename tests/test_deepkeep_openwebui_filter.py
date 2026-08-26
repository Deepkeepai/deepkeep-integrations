import pytest
import respx
from httpx import Response

from deepkeep_openwebui_filter import DeepKeepDecision, DeepKeepError, Filter, _decision_from_response


def make_filter() -> Filter:
    filter_instance = Filter()
    filter_instance.valves.DEEPKEEP_API_KEY = "test-key"
    filter_instance.valves.DEEPKEEP_BASE_URL = "https://api.test.deepkeep.ai"
    filter_instance.valves.PRE_MODEL = "pre-firewall"
    filter_instance.valves.POST_MODEL = "post-firewall"
    return filter_instance


def test_decision_from_response_prefers_block_over_redact() -> None:
    decision = _decision_from_response(
        {
            "verbosity": [
                {"details": {"guardrail_action": "redact", "modified": [{"content": "safe"}]}},
                {"details": {"guardrail_action": "block", "message": "blocked"}},
            ]
        }
    )

    assert decision.action == "block"
    assert decision.reason == "blocked"
    assert decision.modified_content == "safe"


def test_decision_from_response_uses_inputs_fallback() -> None:
    decision = _decision_from_response({"inputs": [{"content": "fallback content"}]})

    assert decision.action is None
    assert decision.modified_content == "fallback content"


@pytest.mark.asyncio
async def test_inlet_replaces_redacted_user_message() -> None:
    filter_instance = make_filter()

    async def fake_moderate(*, path, payload):
        assert path == "/api/v3/openai/moderations/pre"
        assert payload["model"] == "pre-firewall"
        assert payload["input"] == "my secret is 123"
        return DeepKeepDecision(action="redact", modified_content="my secret is [REDACTED]")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "user", "content": "my secret is 123"}]}

    result = await filter_instance.inlet(body)

    assert result["messages"][0]["content"] == "my secret is [REDACTED]"


@pytest.mark.asyncio
async def test_inlet_blocks_user_message() -> None:
    filter_instance = make_filter()
    filter_instance.valves.BLOCK_MESSAGE = "blocked by policy"

    async def fake_moderate(*, path, payload):
        return DeepKeepDecision(action="block")

    filter_instance._moderate = fake_moderate

    with pytest.raises(Exception, match="blocked by policy"):
        await filter_instance.inlet({"messages": [{"role": "user", "content": "bad"}]})


@pytest.mark.asyncio
async def test_outlet_replaces_blocked_assistant_message() -> None:
    filter_instance = make_filter()
    filter_instance.valves.BLOCK_MESSAGE = "blocked output"

    async def fake_moderate(*, path, payload):
        assert path == "/api/v3/openai/moderations/post"
        assert payload["model"] == "post-firewall"
        assert payload["output"] == "unsafe answer"
        return DeepKeepDecision(action="block")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "assistant", "content": "unsafe answer"}]}

    result = await filter_instance.outlet(body)

    assert result["messages"][0]["content"] == "blocked output"


@pytest.mark.asyncio
async def test_outlet_replaces_redacted_assistant_message() -> None:
    filter_instance = make_filter()

    async def fake_moderate(*, path, payload):
        assert path == "/api/v3/openai/moderations/post"
        return DeepKeepDecision(action="redact", modified_content="safe answer")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "assistant", "content": "unsafe answer"}]}

    result = await filter_instance.outlet(body)

    assert result["messages"][0]["content"] == "safe answer"


@pytest.mark.asyncio
async def test_pre_mode_skips_outlet() -> None:
    filter_instance = make_filter()
    filter_instance.valves.MODE = "pre"

    async def fake_moderate(*, path, payload):
        raise AssertionError("outlet should not call DeepKeep in pre mode")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "assistant", "content": "answer"}]}

    result = await filter_instance.outlet(body)

    assert result["messages"][0]["content"] == "answer"


@pytest.mark.asyncio
async def test_post_mode_skips_inlet() -> None:
    filter_instance = make_filter()
    filter_instance.valves.MODE = "post"

    async def fake_moderate(*, path, payload):
        raise AssertionError("inlet should not call DeepKeep in post mode")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "user", "content": "prompt"}]}

    result = await filter_instance.inlet(body)

    assert result["messages"][0]["content"] == "prompt"


@pytest.mark.asyncio
async def test_fail_open_allows_deepkeep_errors() -> None:
    filter_instance = make_filter()
    filter_instance.valves.FAIL_MODE = "fail_open"

    async def fake_moderate(*, path, payload):
        raise RuntimeError("network down")

    filter_instance._moderate = fake_moderate
    body = {"messages": [{"role": "user", "content": "original"}]}

    result = await filter_instance.inlet(body)

    assert result["messages"][0]["content"] == "original"


@pytest.mark.asyncio
async def test_fail_closed_blocks_deepkeep_errors() -> None:
    filter_instance = make_filter()
    filter_instance.valves.FAIL_MODE = "fail_closed"
    filter_instance.valves.BLOCK_MESSAGE = "closed"

    async def fake_moderate(*, path, payload):
        raise RuntimeError("network down")

    filter_instance._moderate = fake_moderate

    with pytest.raises(Exception, match="closed"):
        await filter_instance.inlet({"messages": [{"role": "user", "content": "original"}]})


@pytest.mark.asyncio
@respx.mock
async def test_moderate_posts_to_deepkeep_v3_endpoint() -> None:
    filter_instance = make_filter()
    route = respx.post("https://api.test.deepkeep.ai/api/v3/openai/moderations/pre").mock(
        return_value=Response(
            200,
            json={
                "verbosity": [
                    {
                        "details": {
                            "guardrail_action": "modify",
                            "modified": [{"content": "modified content"}],
                        }
                    }
                ]
            },
        )
    )

    decision = await filter_instance._moderate(
        path="/api/v3/openai/moderations/pre",
        payload={"model": "pre-firewall", "input": "original", "title": "", "chat": "chat-1"},
    )

    assert decision.action == "modify"
    assert decision.modified_content == "modified content"
    assert route.called
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == "test-key"
    assert request.headers["Accept"] == "application/json"
    assert request.url.path == "/api/v3/openai/moderations/pre"
    assert request.content == b'{"model":"pre-firewall","input":"original","title":"","chat":"chat-1"}'


@pytest.mark.asyncio
@respx.mock
async def test_moderate_raises_on_deepkeep_api_error() -> None:
    filter_instance = make_filter()
    respx.post("https://api.test.deepkeep.ai/api/v3/openai/moderations/post").mock(
        return_value=Response(500, text="server error")
    )

    with pytest.raises(DeepKeepError, match="DeepKeep API error 500"):
        await filter_instance._moderate(
            path="/api/v3/openai/moderations/post",
            payload={"model": "post-firewall", "output": "answer", "title": "", "chat": ""},
        )
