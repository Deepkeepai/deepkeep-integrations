# CrewAI Upstream Submission Notes

Recommended repository:

```text
Deepkeepai/crewai-tools-deepkeep
```

Recommended PyPI package:

```text
crewai-tools-deepkeep
```

## Positioning

DeepKeep should be submitted to CrewAI as an external integration docs page, not as new built-in `crewai_tools` classes.

Preferred framing:

> DeepKeep integrates with CrewAI's native task guardrails and execution hooks. It is distributed as an external package, so CrewAI core does not need to maintain vendor-specific API code.

## Why This Diff Should Be Easier To Accept

- It uses `Task.guardrail` / `Task.guardrails`, CrewAI's current native guardrail surface.
- It supports execution hooks for `PRE_MODEL_CALL`, `POST_MODEL_CALL`, `PRE_TOOL_CALL`, and `POST_TOOL_CALL`.
- It does not require CrewAI core changes.
- It does not require adding vendor-specific modules to `crewai_tools`.
- It keeps optional agent-callable tools secondary to runtime enforcement.

## Suggested CrewAI Docs PR

Add a page similar to Portkey, LangDB, Patronus, or the pending Highflame page:

```text
docs/en/observability/deepkeep.mdx
docs/pt-BR/observability/deepkeep.mdx
docs/ko/observability/deepkeep.mdx
docs/ar/observability/deepkeep.mdx
docs/docs.json
```

Suggested page title:

```text
DeepKeep AI Firewall
```

Suggested short description:

```text
Enforce DeepKeep AI Firewall checks in CrewAI using native task guardrails and runtime execution hooks.
```

## PR Checklist

- Publish `crewai-tools-deepkeep` to PyPI first.
- Make the repository public under `Deepkeepai/crewai-tools-deepkeep`.
- Include task guardrail and hook examples in the README.
- Include mocked unit tests for decision parsing and guardrail behavior.
- Keep the CrewAI docs PR documentation-only.
- Avoid requesting changes to CrewAI's guardrail core unless maintainers ask for them.
