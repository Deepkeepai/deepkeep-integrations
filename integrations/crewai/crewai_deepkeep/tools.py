from __future__ import annotations

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .client import DeepKeepClient, decision_from_response


class DeepKeepModerateInputSchema(BaseModel):
    content: str = Field(..., description="User or tool input to moderate before execution.")


class DeepKeepModerateOutputSchema(BaseModel):
    content: str = Field(..., description="Model or tool output to moderate after execution.")


class DeepKeepModerateInputTool(BaseTool):
    name: str = "DeepKeep Moderate Input"
    description: str = "Moderate user or tool input with DeepKeep before it reaches an LLM or tool."
    args_schema: Type[BaseModel] = DeepKeepModerateInputSchema

    api_key: str | None = Field(default=None, description="DeepKeep API key. Defaults to DEEPKEEP_API_KEY.")
    base_url: str | None = Field(default=None, description="DeepKeep base URL. Defaults to DEEPKEEP_BASE_URL.")
    model: str = Field(..., description="DeepKeep input firewall/model ID.")
    title: str = ""
    chat: str = ""
    timeout: float = 30.0

    def _run(self, content: str) -> str:
        client = DeepKeepClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        result = client.pre_moderate(model=self.model, input=content, title=self.title, chat=self.chat)
        decision = decision_from_response(result)
        return decision.reason


class DeepKeepModerateOutputTool(BaseTool):
    name: str = "DeepKeep Moderate Output"
    description: str = "Moderate model or tool output with DeepKeep after generation."
    args_schema: Type[BaseModel] = DeepKeepModerateOutputSchema

    api_key: str | None = Field(default=None, description="DeepKeep API key. Defaults to DEEPKEEP_API_KEY.")
    base_url: str | None = Field(default=None, description="DeepKeep base URL. Defaults to DEEPKEEP_BASE_URL.")
    model: str = Field(..., description="DeepKeep output firewall/model ID.")
    title: str = ""
    chat: str = ""
    timeout: float = 30.0

    def _run(self, content: str) -> str:
        client = DeepKeepClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        result = client.post_moderate(model=self.model, output=content, title=self.title, chat=self.chat)
        decision = decision_from_response(result)
        return decision.reason
