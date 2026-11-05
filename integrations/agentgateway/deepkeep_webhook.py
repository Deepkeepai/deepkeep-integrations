from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


ACTION_PRIORITY = {"block": 4, "redact": 3, "modify": 3, "alert": 1}


class Message(BaseModel):
    role: str
    content: str


class PromptMessages(BaseModel):
    messages: list[Message] = Field(default_factory=list)


class ResponseChoice(BaseModel):
    message: Message


class ResponseChoices(BaseModel):
    choices: list[ResponseChoice] = Field(default_factory=list)


class GuardrailsPromptRequest(BaseModel):
    body: PromptMessages


class GuardrailsResponseRequest(BaseModel):
    body: ResponseChoices


class DeepKeepConfig(BaseModel):
    base_url: str
    api_key: str
    model: str
    title: str = ""
    chat: str = ""
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "DeepKeepConfig":
        base_url = os.environ.get("DEEPKEEP_BASE_URL", "").rstrip("/")
        api_key = os.environ.get("DEEPKEEP_API_KEY", "")
        model = os.environ.get("DEEPKEEP_MODEL", "")
        missing = [
            name
            for name, value in {
                "DEEPKEEP_BASE_URL": base_url,
                "DEEPKEEP_API_KEY": api_key,
                "DEEPKEEP_MODEL": model,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            base_url=base_url,
            api_key=api_key,
            model=model,
            title=os.environ.get("DEEPKEEP_TITLE", ""),
            chat=os.environ.get("DEEPKEEP_CHAT", ""),
            timeout=float(os.environ.get("DEEPKEEP_TIMEOUT", "30")),
        )


class DeepKeepClient:
    def __init__(self, config: DeepKeepConfig) -> None:
        self.config = config

    def pre_moderate(self, text: str) -> dict[str, Any]:
        return self._post("/api/v3/openai/moderations/pre", {"input": text})

    def post_moderate(self, text: str) -> dict[str, Any]:
        return self._post("/api/v3/openai/moderations/post", {"output": text})

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "model": self.config.model,
            **data,
            "title": self.config.title,
            "chat": self.config.chat,
        }
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(
                    f"{self.config.base_url}{path}",
                    headers={"X-API-Key": self.config.api_key, "Accept": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"DeepKeep API error {exc.response.status_code}: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"DeepKeep network error: {exc}") from exc


def create_app(client: DeepKeepClient | None = None) -> FastAPI:
    app = FastAPI(
        title="DeepKeep agentgateway Guardrail Webhook",
        version="0.1.0",
        description="Adapts agentgateway guardrail webhooks to DeepKeep moderation endpoints.",
    )

    deepkeep_client = client or DeepKeepClient(DeepKeepConfig.from_env())

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/request")
    def process_request(req: GuardrailsPromptRequest) -> dict[str, Any]:
        original_text = _join_messages(req.body.messages)
        result = deepkeep_client.pre_moderate(original_text)
        decision = _decision(result)

        if decision.action == "block":
            return {"action": {"body": decision.reason, "status_code": 403, "reason": decision.reason}}
        if decision.action in {"redact", "modify"} and decision.modified_content is not None:
            body = _replace_last_content(req.body, decision.modified_content)
            return {"action": {"body": body.model_dump(), "reason": decision.reason}}
        if decision.unsupported_action:
            reason = f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}"
            return {"action": {"body": reason, "status_code": 403, "reason": reason}}
        return {"action": {"reason": decision.reason}}

    @app.post("/response")
    def process_response(req: GuardrailsResponseRequest) -> dict[str, Any]:
        original_text = _join_choices(req.body.choices)
        result = deepkeep_client.post_moderate(original_text)
        decision = _decision(result)

        if decision.action in {"redact", "modify"} and decision.modified_content is not None:
            body = _replace_last_choice_content(req.body, decision.modified_content)
            return {"action": {"body": body.model_dump(), "reason": decision.reason}}
        if decision.action == "block" or decision.unsupported_action:
            reason = decision.reason
            if decision.unsupported_action:
                reason = f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}"
            return {"action": {"body": _clear_choices(req.body).model_dump(), "reason": reason}}
        return {"action": {"reason": decision.reason}}

    return app


class Decision(BaseModel):
    action: str | None = None
    reason: str = "DeepKeep allowed this content."
    modified_content: str | None = None
    unsupported_action: str | None = None


def _decision(result: dict[str, Any]) -> Decision:
    selected: str | None = None
    unsupported: str | None = None
    reason = "DeepKeep allowed this content."

    for item in result.get("verbosity", []):
        details = item.get("details", {}) if isinstance(item, dict) else {}
        action = details.get("guardrail_action")
        if action is None:
            continue
        if action not in ACTION_PRIORITY:
            unsupported = str(action)
            continue
        if selected is None or ACTION_PRIORITY[action] > ACTION_PRIORITY[selected]:
            selected = action
            reason = details.get("message") or details.get("reason") or item.get("message") or item.get("name") or reason

    return Decision(
        action=selected,
        reason=reason,
        modified_content=_modified_content(result),
        unsupported_action=unsupported if selected is None else None,
    )


def _modified_content(result: dict[str, Any]) -> str | None:
    modified_content: str | None = None
    for item in result.get("verbosity", []):
        details = item.get("details", {}) if isinstance(item, dict) else {}
        for modified in details.get("modified", []):
            content = modified.get("content") if isinstance(modified, dict) else None
            if isinstance(content, str):
                modified_content = content
    if modified_content is not None:
        return modified_content
    inputs = result.get("inputs", [])
    if inputs and isinstance(inputs[0], dict) and isinstance(inputs[0].get("content"), str):
        return inputs[0]["content"]
    return None


def _join_messages(messages: list[Message]) -> str:
    return "\n".join(message.content for message in messages)


def _join_choices(choices: list[ResponseChoice]) -> str:
    return "\n".join(choice.message.content for choice in choices)


def _replace_last_content(body: PromptMessages, content: str) -> PromptMessages:
    updated = body.model_copy(deep=True)
    if updated.messages:
        updated.messages[-1].content = content
    return updated


def _replace_last_choice_content(body: ResponseChoices, content: str) -> ResponseChoices:
    updated = body.model_copy(deep=True)
    if updated.choices:
        updated.choices[-1].message.content = content
    return updated


def _clear_choices(body: ResponseChoices) -> ResponseChoices:
    updated = body.model_copy(deep=True)
    for choice in updated.choices:
        choice.message.content = ""
    return updated


app = create_app()
