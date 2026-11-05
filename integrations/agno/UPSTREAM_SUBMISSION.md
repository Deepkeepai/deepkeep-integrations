# Upstream submission notes

## Target

Ask Agno to list DeepKeep under Guardrails as a custom guardrail integration named DeepKeep AI Firewall.

## Recommended listing

```text
DeepKeep AI Firewall
Use DeepKeep AI Firewall as custom guardrails for Agno Agents and Teams. Add DeepKeepGuardrail to pre_hooks or post_hooks to enforce runtime policies for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks. Supports allow, block, redact, modify, and alert workflows.
```

## Integration surface

DeepKeep should be positioned as a guardrail, not a Toolkit.

Agno Toolkits are model-callable functions. DeepKeep AI Firewall enforcement should run deterministically before or after model execution, so the correct extension point is Agno's `BaseGuardrail` via `pre_hooks` and `post_hooks`.

## Endpoint contract

The Agno package follows the same endpoints as `langchain-deepkeep`:

- `POST /api/v3/openai/moderations/pre`
- `POST /api/v3/openai/moderations/post`
- Header: `X-API-Key: <DEEPKEEP_API_KEY>`
- Pre payload: `{"model": "input-firewall-id", "input": "...", "title": "", "chat": ""}`
- Post payload: `{"model": "output-firewall-id", "output": "...", "title": "", "chat": ""}`

## Suggested Agno issue title

```text
[docs] List DeepKeep AI Firewall as a custom guardrail integration
```

## Suggested Agno PR title

```text
[cookbook] Add DeepKeep AI Firewall guardrails example
```

## Maintainer-facing rationale

DeepKeep is distributed as an external package, so Agno core does not need to maintain vendor-specific API code. The integration uses Agno's documented `BaseGuardrail` custom guardrail API and can be listed as an approved custom guardrail integration once accepted by maintainers.
