# Strands Integration Submission

Status (2026-11-05): [Strands #3996](https://github.com/strands-agents/harness-sdk/pull/3996) merged. The submission notes below are retained for reference; catalog URLs point to the current monorepo directory.

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
github: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands
docsUrl: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands#readme
addedDate: 2026-08-26
maintainedBy: partner
```

DeepKeep is distributed as an external package, so Strands core does not need to maintain vendor-specific API code. The integration uses the documented Strands hook provider interface and is listed in the Strands catalog.
