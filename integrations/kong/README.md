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

- Boolean `flagged: false` -> allow, without consulting action details.
- Boolean `flagged: true` with a nonempty `verbosity` array containing only
  explicit `details.guardrail_action: alert` actions -> allow and report an alert.
- `block`, `redact`, or `modify` -> block. No replacement text is supplied, so
  redaction and modification requests fail closed instead of passing original content.
- Unknown or missing actions -> block (`block_reason: invalid_action`).
- Missing/malformed responses, non-boolean/missing `flagged`, or missing/malformed
  `verbosity`/detail entries on flagged responses -> block (`block_reason: invalid_response`).

All four configurations set `allow_masking: false`; the functions always report
`masked: false`. Mixed actions block if any action is not an explicit alert.
Known action reporting retains priority `block > redact > modify > alert`;
invalid actions take precedence over known actions. String guardrail names are
joined into the singular `block_detail` metric; malformed optional names are ignored.

This is a conservative blocking adapter, not a content-replacement implementation.
The local tests below execute the embedded Lua but do not validate Kong's HTTP,
plugin/template handling, or enforcement in a deployed gateway. Licensed Kong
AI Gateway end-to-end validation remains required.

## Local Tests

From this directory, use Python 3.12 and an isolated environment (with `uv`):

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -c "import sys; from lupa.luajit21 import LuaRuntime; print(sys.version); print(LuaRuntime().eval('jit.version'))"
```

On Unix, substitute `.venv/bin/python` for `.venv/Scripts/python.exe`.
Tests load both Admin API JSON files and both decK plugins and execute each
embedded function with actual LuaJIT 2.1 through `lupa.luajit21`, not a Python
reimplementation. An unavailable LuaJIT module fails collection rather than
silently skipping the tests. No Kong runtime, Docker, license, or API key is
needed for these local policy and configuration-contract tests.

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
- `allow_masking` stays disabled because these functions do not supply replacement content.
- Keep the singular `block_detail` metric key. It is defined in Kong's published [3.14 schema](https://github.com/Kong/developer.konghq.com/blob/main/app/_schemas/gateway/plugins/3.14/AiCustomGuardrail.json), as well as the 3.15 and 3.16 schemas, despite the overview prose using `block_details`.
- If your DeepKeep deployment uses Bearer auth instead of `X-API-Key`, update the header in the examples.
- If you want a docs PR like Lakera's, the usual package is: plugin page, examples, audit-log notes, and a landing-page update.
