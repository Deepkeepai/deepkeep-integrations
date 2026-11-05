# Agno cookbook PR content

Use this content for an Agno cookbook submission.

## Proposed path

```text
cookbook/02_agents/08_guardrails/deepkeep_ai_firewall.py
```

## Proposed file content

```python
"""
DeepKeep AI Firewall Guardrails
===============================

This example shows how to use DeepKeep AI Firewall as custom guardrails for
Agno Agents. DeepKeep runs before user input reaches the model and after model
output is generated.

Set credentials before running:

    export DEEPKEEP_API_KEY="dk_..."
    export DEEPKEEP_BASE_URL="https://api.example.deepkeep.ai"
"""

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno_deepkeep import DeepKeepGuardrail


agent = Agent(
    name="DeepKeep Protected Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    instructions="Answer user questions safely and concisely.",
    pre_hooks=[
        DeepKeepGuardrail(
            pre_model="input-firewall-id",
        )
    ],
    post_hooks=[
        DeepKeepGuardrail(
            post_model="output-firewall-id",
        )
    ],
    markdown=True,
)


if __name__ == "__main__":
    agent.print_response("Explain how to store API keys securely.")
```

## README row

If Agno wants this added to `cookbook/02_agents/README.md`, use:

```md
| DeepKeep AI Firewall | `08_guardrails/deepkeep_ai_firewall.py` | Custom guardrails for DeepKeep AI Firewall input and output moderation |
```

## PR description

```md
Adds a cookbook example showing how to use DeepKeep AI Firewall as Agno custom guardrails.

The example uses the external `agno-deepkeep` package and Agno's native `pre_hooks` and `post_hooks` guardrail extension points. It does not add vendor-specific code to Agno core.
```
