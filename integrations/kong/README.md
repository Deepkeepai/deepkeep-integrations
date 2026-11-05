# DeepKeep Kong Guardrail

This directory packages DeepKeep for Kong AI Gateway's `ai-custom-guardrail` plugin.

Source: [integrations/kong](https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/kong).

```bash
git clone https://github.com/Deepkeepai/deepkeep-integrations.git
cd deepkeep-integrations/integrations/kong
```

The Kong documentation proposal has not been accepted.

## Requirements And Validation

Kong documents this plugin for AI Gateway Enterprise, starting with Gateway
3.14, with an AI Proxy or AI Proxy Advanced route/service. See the
[official plugin requirements](https://developer.konghq.com/plugins/ai-custom-guardrail/).
The checked-in configurations were checked against published field definitions
for 3.14, 3.15, and 3.16; no Kong runtime deployment was exercised.

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
- `guardrail_action: redact` or `modify` -> marks the `masked` metric; replacement-content enforcement is not verified
- `guardrail_action: alert` -> allow and log

**Warning:** The example functions supply no replacement text. Setting
`allow_masking: true` and emitting a `masked` metric is not evidence that Kong
replaces the content. Do not rely on these examples for policies requiring
redaction or modification until an end-to-end test on the intended Kong version
demonstrates enforcement. Runtime behavior was preserved during migration.

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
- `allow_masking` is a valid plugin setting, but the redaction limitation above still applies.
- Keep the singular `block_detail` metric key. It is defined in Kong's published [3.14 schema](https://github.com/Kong/developer.konghq.com/blob/main/app/_schemas/gateway/plugins/3.14/AiCustomGuardrail.json), as well as the 3.15 and 3.16 schemas, despite the overview prose using `block_details`.
- If your DeepKeep deployment uses Bearer auth instead of `X-API-Key`, update the header in the examples.
- If you want a docs PR like Lakera's, the usual package is: plugin page, examples, audit-log notes, and a landing-page update.
