"""DeepKeep LiteLLM custom guardrail integration.

This adapter maps LiteLLM custom guardrail hooks to DeepKeep's two moderation
endpoints:

- pre_call -> /api/v3/openai/moderations/pre
- post_call -> /api/v3/openai/moderations/post

Use this file with LiteLLM's `guardrail: deepkeep_guardrail.DeepKeepGuardrail`
configuration.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence

import httpx
from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.llms.custom_httpx.http_handler import (
    get_async_httpx_client,
    httpxSpecialProvider,
)


class DeepKeepGuardrail(CustomGuardrail):
    SAFE_FALLBACK_MESSAGE = "I'm sorry, but I can't provide that content."

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        firewall_id: Optional[str] = None,
        bearer_token: Optional[str] = None,
        chat: Optional[str] = None,
        title: str = "",
        timeout: float = 10.0,
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPKEEP_API_KEY")
        self.api_base = (api_base or os.getenv("DEEPKEEP_API_BASE") or "").rstrip("/")
        self.firewall_id = firewall_id or os.getenv("DEEPKEEP_FIREWALL_ID")
        self.bearer_token = bearer_token or os.getenv("DEEPKEEP_BEARER_TOKEN")
        self.chat = chat or os.getenv("DEEPKEEP_CHAT", "")
        self.title = title or os.getenv("DEEPKEEP_TITLE", "")
        self.timeout = timeout
        super().__init__(**kwargs)

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        text_items = self._extract_input_texts(data)
        if not text_items:
            return data

        response = await self._moderate(
            endpoint="pre",
            payload_key="input",
            items=text_items,
            request_data=data,
        )
        self._apply_pre_moderation_result(response, data)
        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        text_items = self._extract_output_texts(response)
        if not text_items:
            return None

        result = await self._moderate(
            endpoint="post",
            payload_key="output",
            items=text_items,
            request_data=data,
        )
        return self._apply_post_moderation_result(result, response)

    async def _moderate(
        self,
        endpoint: str,
        payload_key: str,
        items: Sequence[str],
        request_data: Optional[dict],
    ) -> Dict[str, Any]:
        self._require_config()

        params = self.get_guardrail_dynamic_request_body_params(request_data=request_data or {})
        payload: Dict[str, Any] = {
            "model": params.get("model", self.firewall_id),
            payload_key: list(items) if len(items) > 1 else items[0],
            "chat": params.get("chat", self.chat),
            "title": params.get("title", self.title),
        }

        payload.update({k: v for k, v in params.items() if k not in {"model", "chat", "title"}})

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        async_client = get_async_httpx_client(llm_provider=httpxSpecialProvider.LoggingCallback)
        response = await async_client.post(
            f"{self.api_base}/api/v3/openai/moderations/{endpoint}",
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_detail(response)
            raise ValueError(f"DeepKeep moderation request failed: {detail}") from exc

        data = response.json()
        if isinstance(data, dict):
            return data
        return {"result": data}

    def _apply_pre_moderation_result(self, moderation_response: Dict[str, Any], request_data: dict) -> None:
        if not moderation_response or not moderation_response.get("flagged"):
            return

        action, details = self._extract_guardrail_action(moderation_response)
        if action == "block":
            raise ValueError(f"Content blocked by DeepKeep: {self._extract_reason(moderation_response, details)}")

        if action in {"redact", "modify"}:
            updated_texts = self._extract_modified_texts(moderation_response)
            if updated_texts:
                self._replace_request_texts(request_data, updated_texts)

    def _apply_post_moderation_result(self, moderation_response: Dict[str, Any], response: Any) -> Any:
        if not moderation_response or not moderation_response.get("flagged"):
            return response

        action, details = self._extract_guardrail_action(moderation_response)
        if action == "block":
            self._replace_response_texts(response, [self.SAFE_FALLBACK_MESSAGE])
            return response

        if action in {"redact", "modify"}:
            updated_texts = self._extract_modified_texts(moderation_response)
            if updated_texts:
                self._replace_response_texts(response, updated_texts)
            return response

        return response

    def _extract_input_texts(self, request_data: Optional[dict]) -> List[str]:
        if not request_data:
            return []

        messages = request_data.get("messages") or request_data.get("structured_messages") or []
        if not isinstance(messages, list):
            return []

        texts: List[str] = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            if message.get("role") == "system":
                continue
            content = message.get("content")
            extracted = _content_to_text(content)
            if extracted:
                texts.append(extracted)
        return texts

    def _extract_output_texts(self, response: Any) -> List[str]:
        if response is None:
            return []

        if isinstance(response, str):
            return [response] if response else []

        choices = getattr(response, "choices", None)
        if not choices:
            return []

        texts: List[str] = []
        for choice in choices:
            message = getattr(choice, "message", None)
            content = getattr(message, "content", None)
            extracted = _content_to_text(content)
            if extracted:
                texts.append(extracted)
        return texts

    def _extract_guardrail_action(self, moderation_response: Dict[str, Any]) -> tuple[str, Optional[Dict[str, Any]]]:
        verbosity = moderation_response.get("verbosity") or []
        if isinstance(verbosity, list):
            candidates: List[tuple[str, Dict[str, Any]]] = []
            for item in verbosity:
                if not isinstance(item, dict):
                    continue
                details = item.get("details")
                if isinstance(details, dict) and details.get("guardrail_action"):
                    candidates.append((str(details.get("guardrail_action")).lower(), details))
            for preferred in ("block", "redact", "modify", "alert"):
                for action, details in candidates:
                    if action == preferred:
                        return action, details
        return "", None

    def _extract_modified_texts(self, moderation_response: Dict[str, Any]) -> List[str]:
        verbosity = moderation_response.get("verbosity") or []
        if isinstance(verbosity, list):
            texts: List[str] = []
            for item in verbosity:
                if not isinstance(item, dict):
                    continue
                details = item.get("details")
                if not isinstance(details, dict):
                    continue
                modified = details.get("modified")
                if isinstance(modified, list):
                    for entry in modified:
                        if isinstance(entry, dict):
                            content = entry.get("content")
                            if isinstance(content, str) and content:
                                texts.append(content)
                    if texts:
                        return texts
                for key in ("modified_text", "redacted_text", "final_text", "text"):
                    value = details.get(key)
                    if isinstance(value, str) and value:
                        texts.append(value)
                        break
            if texts:
                return texts

        for candidate in (
            moderation_response.get("modified_input"),
            moderation_response.get("modified_output"),
            moderation_response.get("inputs"),
            moderation_response.get("content"),
            moderation_response.get("texts"),
        ):
            texts = _normalize_text_list(candidate)
            if texts:
                return texts

        return []

    def _extract_reason(self, moderation_response: Dict[str, Any], details: Optional[Dict[str, Any]]) -> str:
        if details:
            for key in ("reason", "message", "explanation", "guardrail_reason"):
                value = details.get(key)
                if isinstance(value, str) and value:
                    return value
        for key in ("reason", "message", "blocked_reason"):
            value = moderation_response.get(key)
            if isinstance(value, str) and value:
                return value
        return "DeepKeep guardrail blocked the request"

    def _extract_error_detail(self, response: Any) -> str:
        try:
            payload = response.json()
        except Exception:
            payload = None

        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail:
                return detail
            if isinstance(detail, list) and detail:
                return "; ".join(
                    ",".join(str(part) for part in item.get("loc", [])) + ": " + str(item.get("msg", "validation error"))
                    if isinstance(item, dict)
                    else str(item)
                    for item in detail
                )
            message = payload.get("message")
            if isinstance(message, str) and message:
                return message
        return f"HTTP {getattr(response, 'status_code', 'error')}"

    def _replace_request_texts(self, request_data: dict, updated_texts: List[str]) -> None:
        messages = request_data.get("messages") or []
        if not isinstance(messages, list):
            return

        idx = 0
        for message in messages:
            if not isinstance(message, dict) or message.get("role") == "system":
                continue
            if idx >= len(updated_texts):
                break
            message["content"] = updated_texts[idx]
            idx += 1

    def _replace_response_texts(self, response: Any, updated_texts: List[str]) -> None:
        if not updated_texts:
            return

        choices = getattr(response, "choices", None)
        if not choices:
            if isinstance(response, dict):
                response["content"] = updated_texts[0]
            return

        if len(updated_texts) == 1 and len(choices) > 1:
            updated_texts = updated_texts * len(choices)

        for idx, choice in enumerate(choices):
            text = updated_texts[idx] if idx < len(updated_texts) else updated_texts[-1]
            message = getattr(choice, "message", None)
            if message is not None and hasattr(message, "content"):
                message.content = text
            elif isinstance(choice, dict):
                msg = choice.get("message")
                if isinstance(msg, dict):
                    msg["content"] = text

    def _require_config(self) -> None:
        if not self.api_base:
            raise ValueError("DeepKeep api_base is required")
        if not self.firewall_id:
            raise ValueError("DeepKeep firewall_id is required")
        if not self.api_key and not self.bearer_token:
            raise ValueError("DeepKeep api_key or bearer_token is required")


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif "text" in item:
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
                continue
            parts.append(str(item))
        return "\n".join([part for part in parts if part])
    return str(content)


def _normalize_text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        result: List[str] = []
        for item in value:
            if isinstance(item, str) and item:
                result.append(item)
            elif isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, str) and content:
                    result.append(content)
        return result
    return []


def _env_truthy(name: str) -> bool:
    value = os.getenv(name, "")
    return value.lower() in {"1", "true", "yes", "on"}


__all__ = ["DeepKeepGuardrail"]
