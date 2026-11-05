from __future__ import annotations

from typing import Any

from .client import DeepKeepAPIError, DeepKeepClient, DeepKeepDecision


class DeepKeepHooks:
    """DeepKeep handlers for CrewAI execution hook interception points."""

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

    def check_model_input(self, ctx: Any) -> None:
        if not self.pre_model:
            return None
        decision = self._pre_decision(_messages_text(getattr(ctx, "messages", [])))
        self._enforce_or_mutate_messages(ctx, decision)
        return None

    def check_model_output(self, ctx: Any) -> str | None:
        if not self.post_model:
            return None
        decision = self._post_decision(str(getattr(ctx, "response", "")))
        return self._replacement_or_abort(decision)

    def check_tool_input(self, ctx: Any) -> None:
        if not self.pre_model:
            return None
        decision = self._pre_decision(str(getattr(ctx, "tool_input", "")))
        if decision.should_replace:
            setattr(ctx, "tool_input", decision.modified_content)
        self._abort_if_blocked(decision)
        return None

    def check_tool_output(self, ctx: Any) -> str | None:
        if not self.post_model:
            return None
        value = getattr(ctx, "tool_result", None)
        if value is None:
            value = getattr(ctx, "result", "")
        decision = self._post_decision(str(value))
        return self._replacement_or_abort(decision)

    def _pre_decision(self, text: str) -> DeepKeepDecision:
        try:
            return self.client.pre_decision(model=self.pre_model or "", input=text, title=self.title, chat=self.chat)
        except DeepKeepAPIError as exc:
            return self._handle_error(exc)

    def _post_decision(self, text: str) -> DeepKeepDecision:
        try:
            return self.client.post_decision(model=self.post_model or "", output=text, title=self.title, chat=self.chat)
        except DeepKeepAPIError as exc:
            return self._handle_error(exc)

    def _handle_error(self, exc: DeepKeepAPIError) -> DeepKeepDecision:
        if self.fail_closed:
            return DeepKeepDecision(action="block", reason=str(exc), raw=None)
        return DeepKeepDecision(raw=None)

    def _enforce_or_mutate_messages(self, ctx: Any, decision: DeepKeepDecision) -> None:
        self._abort_if_blocked(decision)
        if decision.should_replace:
            setattr(ctx, "messages", _replace_last_user_message(getattr(ctx, "messages", []), decision.modified_content or ""))

    def _replacement_or_abort(self, decision: DeepKeepDecision) -> str | None:
        self._abort_if_blocked(decision)
        if decision.should_replace:
            return decision.modified_content
        return None

    def _abort_if_blocked(self, decision: DeepKeepDecision) -> None:
        if decision.unsupported_action:
            _raise_hook_aborted(f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}")
        if decision.action == "block":
            _raise_hook_aborted(decision.reason)


def install_deepkeep_hooks(hooks: DeepKeepHooks) -> DeepKeepHooks:
    """Register DeepKeep checks on CrewAI model and tool boundaries."""
    from crewai.hooks import InterceptionPoint, on

    on(InterceptionPoint.PRE_MODEL_CALL)(hooks.check_model_input)
    on(InterceptionPoint.POST_MODEL_CALL)(hooks.check_model_output)
    on(InterceptionPoint.PRE_TOOL_CALL)(hooks.check_tool_input)
    on(InterceptionPoint.POST_TOOL_CALL)(hooks.check_tool_output)
    return hooks


def _raise_hook_aborted(reason: str) -> None:
    from crewai.hooks import HookAborted

    raise HookAborted(reason=reason, source="deepkeep")


def _messages_text(messages: Any) -> str:
    if not messages:
        return ""
    if not isinstance(messages, list):
        return str(messages)
    parts = []
    for message in messages:
        content = _message_content(message)
        if content:
            parts.append(content)
    return "\n".join(parts)


def _message_content(message: Any) -> str:
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return str(content)


def _replace_last_user_message(messages: Any, content: str) -> Any:
    if not isinstance(messages, list):
        return messages
    updated = list(messages)
    for index in range(len(updated) - 1, -1, -1):
        message = updated[index]
        role = message.get("role") if isinstance(message, dict) else getattr(message, "role", None)
        msg_type = message.get("type") if isinstance(message, dict) else getattr(message, "type", None)
        if role == "user" or msg_type == "human":
            updated[index] = _replace_message_content(message, content)
            return updated
    if updated:
        updated[-1] = _replace_message_content(updated[-1], content)
    return updated


def _replace_message_content(message: Any, content: str) -> Any:
    if isinstance(message, dict):
        return {**message, "content": content}
    try:
        return message.__class__(content=content)
    except Exception:
        setattr(message, "content", content)
        return message
