# Open WebUI Community Listing Update

Verified listing: https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e

Edit page: https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e/edit

The listing is published under `@gilharel11159626bf`. The publisher updated its
Repository URL to the monorepo directory; the official public API confirms the
saved update at 2026-11-09 08:43:47 UTC. The embedded code is still version 0.1.1
and matches this repository. The original v0.1.1 GitHub release remains valid and
should remain the Release URL; no replacement Open WebUI release was created here.
The assistant verified public data only and did not use an authenticated editor.

## If The Edit Link Returns Home

The site's root is now a marketing page; its verified Community link points to
https://openwebui.com/home. Sign in directly at
https://openwebui.com/auth?type=login using the original community-account login
method. The current page offers email/password, Google, and GitHub. The
[official community documentation](https://docs.openwebui.com/ecosystem/community/)
confirms this account is separate from a self-hosted Open WebUI account.

After signing in, use the Community page's Profile navigation to check that the
account is `@gilharel11159626bf`, then retry the edit link above. Authenticated
editor controls have not been inspected, so do not assume a particular tab or
form label. Do not create a duplicate account/listing to work around an edit issue.

If the correct publisher account still redirects home, ask through the
[official Discord](https://discord.gg/5rJgQTnV4s) for the supported editor or
website-bug reporting route. A dedicated website issue tracker/channel was not
verified. Include the public post ID and redirect behavior, but no credentials.

## Minimal Migration Edit

The Repository link below is now updated. The Raw Function URL is optional.
Preserve the embedded function and version:
the published 0.1.1 code matches the migrated source. Keep the existing
`https://github.com/Deepkeepai/openwebui-deepkeep/releases/tag/v0.1.1` link as a
historical release reference; the monorepo has not published a replacement release.
Do not create a duplicate listing. The fuller text below is available if the
publisher wants to refresh the description separately.

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

https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/openwebui

## Raw Function URL

https://raw.githubusercontent.com/Deepkeepai/deepkeep-integrations/main/integrations/openwebui/deepkeep_openwebui_filter.py

## Tags

deepkeep, firewall, guardrails, moderation, pii, redaction, security, compliance, filter
