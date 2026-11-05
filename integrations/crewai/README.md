# crewai-tools-deepkeep

DeepKeep AI Firewall integration for CrewAI native guardrails and execution hooks.

This package is designed as an external CrewAI integration, not a patch to `crewai_tools`. It follows CrewAI's native extension points:

- `Task.guardrail` / `Task.guardrails` for task output validation and retry feedback.
- Execution hooks for pre/post LLM and tool-call enforcement.
- Optional CrewAI tools for agent-driven moderation workflows.

## Installation

```bash
pip install crewai-tools-deepkeep
```

Set credentials:

```bash
export DEEPKEEP_API_KEY="dk_..."
export DEEPKEEP_BASE_URL="https://api.example.deepkeep.ai"
```

## Task Guardrail

Use this when you want CrewAI to validate task output and retry the task when DeepKeep blocks it.

```python
from crewai import Agent, Task
from crewai_deepkeep import DeepKeepGuardrail

deepkeep = DeepKeepGuardrail(
    post_model="output-firewall-id",
)

task = Task(
    description="Answer the user safely.",
    expected_output="A safe answer.",
    agent=agent,
    guardrail=deepkeep.check_output,
    guardrail_max_retries=3,
)
```

`DeepKeepGuardrail.check_output` returns CrewAI's expected guardrail tuple:

```python
(True, validated_or_modified_output)
(False, "feedback for the agent retry")
```

## Runtime Hooks

Use this when you want DeepKeep to enforce policy around every model and tool boundary.

```python
from crewai_deepkeep import DeepKeepHooks, install_deepkeep_hooks

install_deepkeep_hooks(
    DeepKeepHooks(
        pre_model="input-firewall-id",
        post_model="output-firewall-id",
    )
)
```

This registers checks for:

- `PRE_MODEL_CALL`
- `POST_MODEL_CALL`
- `PRE_TOOL_CALL`
- `POST_TOOL_CALL`

Blocking decisions raise CrewAI `HookAborted` with `source="deepkeep"`. Redact/modify decisions replace the intercepted message, response, tool input, or tool result where CrewAI supports replacement.

## Manual Hook Registration

If you prefer explicit registration:

```python
from crewai.hooks import InterceptionPoint, on
from crewai_deepkeep import DeepKeepHooks

hooks = DeepKeepHooks(pre_model="input-firewall-id", post_model="output-firewall-id")

on(InterceptionPoint.PRE_MODEL_CALL)(hooks.check_model_input)
on(InterceptionPoint.POST_MODEL_CALL)(hooks.check_model_output)
on(InterceptionPoint.PRE_TOOL_CALL)(hooks.check_tool_input)
on(InterceptionPoint.POST_TOOL_CALL)(hooks.check_tool_output)
```

## Optional Tools

Tools are available for workflows where the agent should explicitly call DeepKeep:

```python
from crewai_deepkeep.tools import DeepKeepModerateInputTool

agent = Agent(
    role="AI Security Guard",
    tools=[DeepKeepModerateInputTool(model="input-firewall-id")],
)
```

For production enforcement, prefer task guardrails and hooks over agent-callable tools.

## Recommended CrewAI Docs Positioning

Status (2026-11-05): [CrewAI docs #7202](https://github.com/crewAIInc/crewAI/pull/7202) closed unmerged. [Maintainers requested a vendor-hosted guide](https://github.com/crewAIInc/crewAI/pull/7202#issuecomment-5508136001); this README is the integration guide. External integration positioning:

```text
DeepKeep integrates with CrewAI's native task guardrails and execution hooks. It is distributed as an external package, so CrewAI core does not need to maintain vendor-specific API code.
```

## Environment Variables

- `DEEPKEEP_API_KEY`: DeepKeep API key.
- `DEEPKEEP_BASE_URL`: DeepKeep API base URL, without a trailing slash.

## Repository Placement

Canonical integration directory:

```text
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/crewai
```
