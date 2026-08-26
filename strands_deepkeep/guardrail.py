from __future__ import annotations

import os
from typing import Any

import httpx

try:
    from strands.plugins import Plugin
except ModuleNotFoundError:  # pragma: no cover - used only when Strands is not installed in a test environment.
    class Plugin:  # type: ignore[no-redef]
        def __init__(self) -> None:
            pass


class DeepKeepAPIError(Exception):
    """Raised when the DeepKeep API returns an error or a network request fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class DeepKeepClient:
    """HTTP client for DeepKeep OpenAI-compatible moderation endpoints."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPKEEP_API_KEY")
        self.base_url = (base_url or os.environ.get("DEEPKEEP_BASE_URL") or "").rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("DeepKeep API key is required. Pass api_key or set DEEPKEEP_API_KEY.")
        if not self.base_url:
            raise ValueError("DeepKeep base URL is required. Pass base_url or set DEEPKEEP_BASE_URL.")

    def pre_moderate(
        self,
        *,
        model: str,
        input: str | list[str],
        title: str = "",
        chat: str = "",
    ) -> dict[str, Any]:
        return self._post(
            "/api/v3/openai/moderations/pre",
            {"model": model, "input": input, "title": title, "chat": chat},
        )

    def post_moderate(
        self,
        *,
        model: str,
        output: str | list[str],
        title: str = "",
        chat: str = "",
    ) -> dict[str, Any]:
        return self._post(
            "/api/v3/openai/moderations/post",
            {"model": model, "output": output, "title": title, "chat": chat},
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}{path}",
                    headers={"X-API-Key": self.api_key},
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise DeepKeepAPIError(f"DeepKeep network error: {exc}") from exc

        if response.status_code >= 400:
            raise DeepKeepAPIError(
                f"DeepKeep API error {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        return response.json()


class DeepKeepGuardrail(Plugin):
    """Strands hook provider that applies DeepKeep pre- and post-moderation."""

    @property
    def name(self) -> str:
        return "deepkeep-guardrail"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        pre_model: str | None = None,
        post_model: str | None = None,
        title: str = "",
        chat: str = "",
        timeout: float = 30.0,
        block_message: str = "DeepKeep blocked this content.",
    ) -> None:
        if not pre_model and not post_model:
            raise ValueError("At least one of pre_model or post_model is required.")

        super().__init__()

        self.client = DeepKeepClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self.pre_model = pre_model
        self.post_model = post_model
        self.title = title
        self.chat = chat
        self.block_message = block_message

    def register_hooks(self, registry: Any) -> None:
        from strands.hooks import AfterModelCallEvent, BeforeInvocationEvent

        if self.pre_model:
            registry.add_callback(BeforeInvocationEvent, self.before_invocation)
        if self.post_model:
            registry.add_callback(AfterModelCallEvent, self.after_model_call)

    def init_agent(self, agent: Any) -> None:
        from strands.hooks import AfterModelCallEvent, BeforeInvocationEvent

        if self.pre_model:
            agent.add_hook(self.before_invocation, BeforeInvocationEvent)
        if self.post_model:
            agent.add_hook(self.after_model_call, AfterModelCallEvent)

    def before_invocation(self, event: Any) -> None:
        messages = getattr(event, "messages", None)
        content = _last_user_text(messages)
        result = self.client.pre_moderate(
            model=self.pre_model or "",
            input=content,
            title=self.title,
            chat=self.chat,
        )
        _store_decision(event, "deepkeep_pre", result)

        action = _highest_priority_action(result)
        if action == "block":
            event.cancel = self.block_message
        elif action in {"redact", "modify"} and messages is not None:
            event.messages = _replace_last_user_text(messages, _modified_content(result))

    def after_model_call(self, event: Any) -> None:
        stop_response = getattr(event, "stop_response", None)
        message = getattr(stop_response, "message", None)
        content = _message_text(message)
        result = self.client.post_moderate(
            model=self.post_model or "",
            output=content,
            title=self.title,
            chat=self.chat,
        )
        _store_decision(event, "deepkeep_post", result)

        action = _highest_priority_action(result)
        if action == "block" and message is not None:
            _replace_message_text(message, "")
            _add_message_metadata(message, result)
        elif action in {"redact", "modify"} and message is not None:
            _replace_message_text(message, _modified_content(result))
            _add_message_metadata(message, result)


def _store_decision(event: Any, key: str, result: dict[str, Any]) -> None:
    invocation_state = getattr(event, "invocation_state", None)
    if isinstance(invocation_state, dict):
        invocation_state[key] = result


def _last_user_text(messages: Any) -> str:
    if not messages:
        return ""
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return _message_text(message)
    return _message_text(messages[-1])


def _message_text(message: Any) -> str:
    if not isinstance(message, dict):
        return ""
    parts: list[str] = []
    for block in message.get("content", []):
        if isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "\n".join(parts)


def _replace_last_user_text(messages: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
    updated = [dict(message) for message in messages]
    for index in range(len(updated) - 1, -1, -1):
        if updated[index].get("role") == "user":
            _replace_message_text(updated[index], text)
            return updated
    if updated:
        _replace_message_text(updated[-1], text)
    return updated


def _replace_message_text(message: dict[str, Any], text: str) -> None:
    content = message.get("content")
    if not isinstance(content, list):
        message["content"] = [{"text": text}]
        return

    for block in content:
        if isinstance(block, dict) and "text" in block:
            block["text"] = text
            return
    content.insert(0, {"text": text})


def _add_message_metadata(message: dict[str, Any], result: dict[str, Any]) -> None:
    metadata = message.setdefault("metadata", {})
    custom = metadata.setdefault("custom", {})
    custom["deepkeep"] = result


def _highest_priority_action(result: dict[str, Any]) -> str | None:
    priority = {"block": 3, "redact": 2, "modify": 2, "alert": 1}
    selected: str | None = None
    for item in result.get("verbosity", []):
        action = item.get("details", {}).get("guardrail_action")
        if action in priority and (selected is None or priority[action] > priority[selected]):
            selected = action
    return selected


def _modified_content(result: dict[str, Any]) -> str:
    modified_content: str | None = None
    for item in result.get("verbosity", []):
        for modified in item.get("details", {}).get("modified", []):
            content = modified.get("content")
            if isinstance(content, str):
                modified_content = content
    if modified_content is not None:
        return modified_content
    inputs = result.get("inputs", [])
    if inputs and isinstance(inputs[0], dict) and isinstance(inputs[0].get("content"), str):
        return inputs[0]["content"]
    return ""
