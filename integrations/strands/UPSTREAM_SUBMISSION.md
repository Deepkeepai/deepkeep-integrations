# Strands Integration Submission

Ask Strands Agents to list DeepKeep under plugins as a reusable guardrail integration named DeepKeep AI Firewall.

## Positioning

DeepKeep AI Firewall

Use [DeepKeep AI Firewall](https://deepkeep.ai/capabilities/ai-firewall) as runtime guardrails for Strands Agents. Add `DeepKeepGuardrail` as a plugin to run DeepKeep pre-moderation before agent input reaches the model and post-moderation after model responses. Supports allow, block, redact, modify, and alert workflows for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.

## Why plugin

DeepKeep enforcement should run deterministically around agent invocations and model responses. Strands plugins are the documented packaging mechanism for multiple lifecycle hooks, and `BeforeInvocationEvent` plus `AfterModelCallEvent` provide the correct extension points.

## Catalog file

Create `site/src/content/catalog/strands-deepkeep.yaml`:

```yaml
name: strands-deepkeep
description: DeepKeep AI Firewall guardrails for Strands Agents using lifecycle hooks around model input and output.
integrationType: plugin
languages:
  python:
    package: strands-deepkeep
github: https://github.com/Deepkeepai/strands-deepkeep
docsUrl: https://github.com/Deepkeepai/strands-deepkeep#readme
addedDate: 2026-08-26
maintainedBy: partner
```

DeepKeep is distributed as an external package, so Strands core does not need to maintain vendor-specific API code. The integration uses the documented Strands hook provider interface and can be listed as an approved plugin once accepted by maintainers.
