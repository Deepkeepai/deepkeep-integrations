# Open WebUI Community Listing Draft

## Title

DeepKeep AI Firewall Filter

## Type

Function: Filter

## Short Description

Always-on Open WebUI filter for DeepKeep AI Firewall using v3 pre/post moderation endpoints.

## Description

DeepKeep AI Firewall Filter adds pre-model and post-model moderation to Open WebUI through a native Filter Function.

It checks user prompts before they reach the model and assistant responses before they are shown to users. Based on DeepKeep policy decisions, the filter can block, redact, modify, alert, or allow content.

The filter is designed for security and compliance use cases, so it is always-on when active and does not expose a user chat toggle.

## Features

- Pre-model prompt moderation with `/api/v3/openai/moderations/pre`.
- Post-model response moderation with `/api/v3/openai/moderations/post`.
- Supports DeepKeep actions: `block`, `redact`, `modify`, and `alert`.
- Admin-configurable Open WebUI Valves for API key, base URL, models, mode, timeout, fail behavior, and block message.
- Supports `pre`, `post`, and `both` modes.
- Supports `fail_closed` for mandatory enforcement and `fail_open` for availability-first deployments.
- Includes local tests and a direct DeepKeep v3 smoke-test script.

## Requirements

- Open WebUI with Function support.
- Python package: `httpx`.
- DeepKeep API key.
- DeepKeep v3 base URL.
- DeepKeep pre and/or post model/firewall identifiers.

## Configuration

Configure these valves after import:

- `DEEPKEEP_API_KEY`
- `DEEPKEEP_BASE_URL`
- `PRE_MODEL`
- `POST_MODEL`
- `MODE`
- `FAIL_MODE`
- `BLOCK_MESSAGE`
- `TIMEOUT`
- `priority`

## Recommended Usage

Enable the filter globally for mandatory firewall enforcement across Open WebUI models.

Use `MODE=both` and `FAIL_MODE=fail_closed` for strict pre/post moderation.

## Repository URL

https://github.com/gilarel/openwebui-deepkeep

## Raw Function URL

https://raw.githubusercontent.com/gilarel/openwebui-deepkeep/main/deepkeep_openwebui_filter.py

## Tags

deepkeep, firewall, guardrails, moderation, pii, redaction, security, compliance, filter
