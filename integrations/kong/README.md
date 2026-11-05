# DeepKeep Kong Guardrail

This repo packages DeepKeep for Kong AI Gateway's `ai-custom-guardrail` plugin.

## Mapping

- `INPUT` -> `POST /api/v3/openai/moderations/pre`
- `OUTPUT` -> `POST /api/v3/openai/moderations/post`
- `model` -> DeepKeep firewall id
- `input` -> prompt text for pre-moderation
- `output` -> model text for post-moderation
- `chat` and `title` are optional metadata fields

## DeepKeep actions

- `flagged: false` -> allow
- `guardrail_action: block` -> block
- `guardrail_action: redact` or `modify` -> mask when `allow_masking: true`
- `guardrail_action: alert` -> allow and log

## Files

- `examples/deck/deepkeep-ai-guardrails.yaml`
- `examples/admin-api/input.json`
- `examples/admin-api/output.json`
- `examples/kong-docs-submission.md`

## Environment variables

- `DEEPKEEP_API_BASE`
- `DEEPKEEP_API_KEY`
- `DEEPKEEP_INPUT_FIREWALL_ID`
- `DEEPKEEP_OUTPUT_FIREWALL_ID`

Optional:

- `DEEPKEEP_CHAT_ID`
- `DEEPKEEP_TITLE`

## Notes

- The Kong plugin still requires an `AI Proxy` or `AI Proxy Advanced` route/service.
- The deck example assumes an existing service named `example-ai-service`; replace it with your AI Proxy service or route.
- `allow_masking: true` is the Kong knob for DeepKeep redaction-style outcomes.
- If your DeepKeep deployment uses Bearer auth instead of `X-API-Key`, update the header in the examples.
- If you want a docs PR like Lakera's, the usual package is: plugin page, examples, audit-log notes, and a landing-page update.
