from __future__ import annotations

from typing import Any

from .client import DeepKeepAPIError, DeepKeepClient, DeepKeepDecision


class DeepKeepGuardrail:
    """CrewAI task guardrail adapter for DeepKeep output moderation."""

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
        fail_closed: bool = True,
    ) -> None:
        if not pre_model and not post_model:
            raise ValueError("At least one of pre_model or post_model is required.")
        self.client = DeepKeepClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self.pre_model = pre_model
        self.post_model = post_model
        self.title = title
        self.chat = chat
        self.fail_closed = fail_closed

    def check_output(self, result: Any) -> tuple[bool, Any]:
        """Validate a CrewAI TaskOutput using DeepKeep post-moderation."""
        if not self.post_model:
            return True, result

        text = _task_output_text(result)
        try:
            decision = self.client.post_decision(
                model=self.post_model,
                output=text,
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                return False, str(exc)
            return True, result

        return _guardrail_tuple(result, decision)

    def check_input(self, result: Any) -> tuple[bool, Any]:
        """Validate a CrewAI TaskOutput-like value using DeepKeep pre-moderation."""
        if not self.pre_model:
            return True, result

        text = _task_output_text(result)
        try:
            decision = self.client.pre_decision(
                model=self.pre_model,
                input=text,
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                return False, str(exc)
            return True, result

        return _guardrail_tuple(result, decision)

    def __call__(self, result: Any) -> tuple[bool, Any]:
        return self.check_output(result)


def _guardrail_tuple(original: Any, decision: DeepKeepDecision) -> tuple[bool, Any]:
    if decision.unsupported_action:
        return False, f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}"
    if decision.action == "block":
        return False, decision.reason
    if decision.should_replace:
        return True, decision.modified_content
    return True, original


def _task_output_text(result: Any) -> str:
    raw = getattr(result, "raw", None)
    if isinstance(raw, str):
        return raw
    if raw is not None:
        return str(raw)
    if isinstance(result, str):
        return result
    return str(result)
