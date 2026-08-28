"""
title: DeepKeep AI Firewall
author: DeepKeep
version: 0.1.1
description: Always-on Open WebUI filter for DeepKeep v3 pre/post moderation.
requirements: httpx
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

import httpx
from pydantic import BaseModel, Field


ACTION_PRIORITY = {"block": 4, "redact": 3, "modify": 3, "alert": 1}


class DeepKeepError(Exception):
    pass


@dataclass(frozen=True)
class DeepKeepDecision:
    action: Optional[str] = None
    reason: str = "DeepKeep allowed this content."
    modified_content: Optional[str] = None
    unsupported_action: Optional[str] = None

    @property
    def should_replace(self) -> bool:
        return self.action in {"redact", "modify"} and self.modified_content is not None


class Filter:
    class Valves(BaseModel):
        DEEPKEEP_API_KEY: str = Field(
            default="",
            description="DeepKeep API key.",
            json_schema_extra={"input": {"type": "password"}},
        )
        DEEPKEEP_BASE_URL: str = Field(
            default="",
            description="DeepKeep base URL, for example https://api.example.deepkeep.ai.",
        )
        PRE_MODEL: str = Field(
            default="",
            description="DeepKeep model/firewall identifier for pre-moderation.",
        )
        POST_MODEL: str = Field(
            default="",
            description="DeepKeep model/firewall identifier for post-moderation.",
        )
        MODE: Literal["pre", "post", "both"] = Field(
            default="both",
            description="Run DeepKeep before the model, after the model, or both.",
        )
        FAIL_MODE: Literal["fail_closed", "fail_open"] = Field(
            default="fail_closed",
            description="Block on DeepKeep errors, or allow original content through.",
        )
        BLOCK_MESSAGE: str = Field(
            default="This message was blocked by DeepKeep AI Firewall.",
            description="Message shown when DeepKeep blocks content or fail-closed triggers.",
        )
        TIMEOUT: float = Field(default=30.0, description="DeepKeep HTTP timeout in seconds.")
        priority: int = Field(default=0, description="Filter execution order. Lower values run first.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def inlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __metadata__: Optional[dict] = None,
    ) -> dict:
        if self.valves.MODE not in {"pre", "both"}:
            return body

        message = _last_message(body.get("messages", []), "user")
        if not message:
            return body

        content = _content_to_text(message.get("content"))
        if not content:
            return body

        try:
            decision = await self._moderate(
                path="/api/v3/openai/moderations/pre",
                payload={
                    "model": self._required_model("PRE_MODEL"),
                    "input": content,
                    "title": _title_from_metadata(__metadata__),
                    "chat": _chat_from_metadata(__metadata__),
                },
            )
        except Exception as exc:
            if self.valves.FAIL_MODE == "fail_open":
                return body
            raise Exception(self.valves.BLOCK_MESSAGE) from exc

        if decision.unsupported_action:
            if self.valves.FAIL_MODE == "fail_open":
                return body
            raise Exception(f"Unsupported DeepKeep action: {decision.unsupported_action}")
        if decision.action == "block":
            raise Exception(self.valves.BLOCK_MESSAGE)
        if decision.should_replace:
            message["content"] = decision.modified_content

        return body

    async def outlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __metadata__: Optional[dict] = None,
    ) -> dict:
        if self.valves.MODE not in {"post", "both"}:
            return body

        message = _last_message(body.get("messages", []), "assistant")
        if not message:
            return body

        content = _content_to_text(message.get("content"))
        if not content:
            return body

        try:
            decision = await self._moderate(
                path="/api/v3/openai/moderations/post",
                payload={
                    "model": self._required_model("POST_MODEL"),
                    "output": content,
                    "title": _title_from_metadata(__metadata__),
                    "chat": _chat_from_metadata(__metadata__),
                },
            )
        except Exception as exc:
            if self.valves.FAIL_MODE == "fail_open":
                return body
            message["content"] = self.valves.BLOCK_MESSAGE
            return body

        if decision.unsupported_action:
            if self.valves.FAIL_MODE == "fail_closed":
                message["content"] = self.valves.BLOCK_MESSAGE
            return body
        if decision.action == "block":
            message["content"] = self.valves.BLOCK_MESSAGE
        elif decision.should_replace:
            message["content"] = decision.modified_content

        return body

    async def _moderate(self, *, path: str, payload: dict[str, Any]) -> DeepKeepDecision:
        api_key = self.valves.DEEPKEEP_API_KEY.strip()
        base_url = self.valves.DEEPKEEP_BASE_URL.strip().rstrip("/")
        if not api_key:
            raise DeepKeepError("DeepKeep API key is required.")
        if not base_url:
            raise DeepKeepError("DeepKeep base URL is required.")

        try:
            async with httpx.AsyncClient(timeout=self.valves.TIMEOUT) as client:
                response = await client.post(
                    f"{base_url}{path}",
                    headers={"X-API-Key": api_key, "Accept": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise DeepKeepError(f"DeepKeep network error: {exc}") from exc

        if response.status_code >= 400:
            raise DeepKeepError(f"DeepKeep API error {response.status_code}: {response.text}")

        return _decision_from_response(response.json())

    def _required_model(self, valve_name: Literal["PRE_MODEL", "POST_MODEL"]) -> str:
        model = getattr(self.valves, valve_name).strip()
        if not model:
            raise DeepKeepError(f"{valve_name} is required for DeepKeep moderation.")
        return model


def _decision_from_response(result: dict[str, Any]) -> DeepKeepDecision:
    selected: Optional[str] = None
    unsupported: Optional[str] = None
    reason = "DeepKeep allowed this content."
    modified_content: Optional[str] = None

    for item in result.get("verbosity", []):
        if not isinstance(item, dict):
            continue
        details = item.get("details", {}) if isinstance(item.get("details"), dict) else {}
        action = details.get("guardrail_action")
        if action is None:
            continue
        if action not in ACTION_PRIORITY:
            unsupported = str(action)
            continue
        if selected is None or ACTION_PRIORITY[action] > ACTION_PRIORITY[selected]:
            selected = action
            reason = details.get("message") or details.get("reason") or item.get("message") or item.get("name") or reason

        for modified in details.get("modified", []) or []:
            if isinstance(modified, dict) and isinstance(modified.get("content"), str):
                modified_content = modified["content"]

    if modified_content is None:
        inputs = result.get("inputs", [])
        if inputs and isinstance(inputs[0], dict) and isinstance(inputs[0].get("content"), str):
            modified_content = inputs[0]["content"]

    return DeepKeepDecision(
        action=selected,
        reason=reason,
        modified_content=modified_content,
        unsupported_action=unsupported,
    )


def _last_message(messages: Any, role: str) -> Optional[dict[str, Any]]:
    if not isinstance(messages, list):
        return None
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == role:
            return message
    return None


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return "" if content is None else str(content)


def _title_from_metadata(metadata: Optional[dict]) -> str:
    if not metadata:
        return ""
    title = metadata.get("title") or metadata.get("chat_title") or metadata.get("name")
    return title if isinstance(title, str) else ""


def _chat_from_metadata(metadata: Optional[dict]) -> str:
    if not metadata:
        return ""
    chat_id = metadata.get("chat_id")
    return chat_id if isinstance(chat_id, str) else ""
