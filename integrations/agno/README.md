# agno-deepkeep

DeepKeep AI Firewall custom guardrails for Agno.

This package follows Agno's native guardrail extension point. Add `DeepKeepGuardrail` to an Agent or Team with `pre_hooks` to check input before it reaches the model, or with `post_hooks` to check output before it is returned.

## Installation

```bash
pip install agno-deepkeep
```

Set credentials:

```bash
export DEEPKEEP_API_KEY="dk_..."
export DEEPKEEP_BASE_URL="https://api.example.deepkeep.ai"
```

## Input guardrails

Use `pre_hooks` to run DeepKeep pre-moderation before an Agno Agent or Team processes user input:

```python
from agno.agent import Agent
from agno_deepkeep import DeepKeepGuardrail

agent = Agent(
    name="DeepKeep Protected Agent",
    model="openai:gpt-5.2",
    pre_hooks=[
        DeepKeepGuardrail(
            pre_model="input-firewall-id",
        )
    ],
)
```

## Output guardrails

Use `post_hooks` to run DeepKeep post-moderation after the model response is generated:

```python
from agno.agent import Agent
from agno_deepkeep import DeepKeepGuardrail

agent = Agent(
    name="DeepKeep Protected Agent",
    model="openai:gpt-5.2",
    post_hooks=[
        DeepKeepGuardrail(
            post_model="output-firewall-id",
        )
    ],
)
```

## Input and output protection

Use separate instances when you want distinct firewall IDs for input and output checks:

```python
from agno.agent import Agent
from agno_deepkeep import DeepKeepGuardrail

agent = Agent(
    name="DeepKeep Protected Agent",
    model="openai:gpt-5.2",
    pre_hooks=[DeepKeepGuardrail(pre_model="input-firewall-id")],
    post_hooks=[DeepKeepGuardrail(post_model="output-firewall-id")],
)
```

## DeepKeep endpoints

This package uses the same DeepKeep OpenAI-compatible moderation endpoints as the LangChain integration:

- `POST /api/v3/openai/moderations/pre` with `{"model", "input", "title", "chat"}`.
- `POST /api/v3/openai/moderations/post` with `{"model", "output", "title", "chat"}`.
- `X-API-Key` for authentication.

`pre_model` and `post_model` are DeepKeep firewall IDs. Each value is sent to the matching moderation endpoint as the `model` field.

## Guardrail actions

DeepKeep responses are interpreted from `verbosity[].details.guardrail_action`:

- `block`: Raises Agno `InputCheckError` or `OutputCheckError`.
- `redact` or `modify`: Replaces Agno input or output when DeepKeep returns modified content.
- `alert`: Allows the run to continue.

If DeepKeep returns an unsupported action, the guardrail fails closed.

## Configuration

- `api_key`: DeepKeep API key. If omitted, reads `DEEPKEEP_API_KEY`.
- `base_url`: DeepKeep base URL, without a trailing slash. If omitted, reads `DEEPKEEP_BASE_URL`.
- `pre_model`: DeepKeep firewall ID for pre-moderation.
- `post_model`: DeepKeep firewall ID for post-moderation.
- `title`: Optional title value sent to DeepKeep.
- `chat`: Optional chat value sent to DeepKeep.
- `timeout`: Request timeout in seconds. Defaults to `30.0`.
- `fail_closed`: Raise a guardrail error when DeepKeep cannot be reached. Defaults to `True`.

## Recommended Agno docs positioning

Position the public integration as DeepKeep AI Firewall in Agno's custom guardrails area:

```text
DeepKeep AI Firewall
Use DeepKeep AI Firewall as custom guardrails for Agno Agents and Teams. Add DeepKeepGuardrail to pre_hooks or post_hooks to enforce runtime policies for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.
```

For production enforcement, prefer Agno guardrails over agent-callable tools because guardrails run deterministically before or after model execution.
