from __future__ import annotations

from typing import Any

from agno.exceptions import CheckTrigger, InputCheckError, OutputCheckError
from agno.guardrails import BaseGuardrail

from .client import DeepKeepAPIError, DeepKeepClient, DeepKeepDecision


class DeepKeepGuardrail(BaseGuardrail):
    """Agno guardrail adapter for DeepKeep AI Firewall moderation."""

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

    def check(self, run_input: Any = None, run_output: Any = None) -> None:
        """Run DeepKeep moderation against Agno Agent or Team input or output."""
        if run_output is not None:
            self.check_output(run_output)
            return
        if run_input is None or not self.pre_model:
            return

        try:
            decision = self.client.pre_decision(
                model=self.pre_model,
                input=run_input.input_content_string(),
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                raise InputCheckError(str(exc), check_trigger=CheckTrigger.INPUT_NOT_ALLOWED) from exc
            return

        _apply_input_decision(run_input, decision)

    async def async_check(self, run_input: Any = None, run_output: Any = None) -> None:
        """Run DeepKeep async moderation against Agno Agent or Team input or output."""
        if run_output is not None:
            await self.async_check_output(run_output)
            return
        if run_input is None or not self.pre_model:
            return

        try:
            decision = await self.client.async_pre_decision(
                model=self.pre_model,
                input=run_input.input_content_string(),
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                raise InputCheckError(str(exc), check_trigger=CheckTrigger.INPUT_NOT_ALLOWED) from exc
            return

        _apply_input_decision(run_input, decision)

    def check_output(self, run_output: Any) -> None:
        """Run DeepKeep post-moderation against Agno Agent or Team output."""
        if not self.post_model:
            return

        try:
            decision = self.client.post_decision(
                model=self.post_model,
                output=_output_content_string(run_output),
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                raise OutputCheckError(str(exc), check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED) from exc
            return

        _apply_output_decision(run_output, decision)

    async def async_check_output(self, run_output: Any) -> None:
        """Run DeepKeep async post-moderation against Agno Agent or Team output."""
        if not self.post_model:
            return

        try:
            decision = await self.client.async_post_decision(
                model=self.post_model,
                output=_output_content_string(run_output),
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError as exc:
            if self.fail_closed:
                raise OutputCheckError(str(exc), check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED) from exc
            return

        _apply_output_decision(run_output, decision)


def _apply_input_decision(run_input: Any, decision: DeepKeepDecision) -> None:
    if decision.unsupported_action:
        raise InputCheckError(
            f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}",
            check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
            additional_data=decision.raw,
        )
    if decision.action == "block":
        raise InputCheckError(
            decision.reason,
            check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
            additional_data=decision.raw,
        )
    if decision.should_replace:
        run_input.input_content = decision.modified_content


def _apply_output_decision(run_output: Any, decision: DeepKeepDecision) -> None:
    if decision.unsupported_action:
        raise OutputCheckError(
            f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}",
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
            additional_data=decision.raw,
        )
    if decision.action == "block":
        raise OutputCheckError(
            decision.reason,
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
            additional_data=decision.raw,
        )
    if decision.should_replace:
        _set_output_content(run_output, decision.modified_content)


def _output_content_string(run_output: Any) -> str:
    content = getattr(run_output, "content", None)
    if isinstance(content, str):
        return content
    if content is not None:
        return str(content)
    return str(run_output)


def _set_output_content(run_output: Any, content: str | None) -> None:
    if content is None:
        return
    if hasattr(run_output, "content"):
        run_output.content = content
