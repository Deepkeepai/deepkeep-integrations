# DeepKeep Portkey Partner Guardrail

This repo contains a Portkey partner-guardrail plugin for DeepKeep.

## What it does

- Calls DeepKeep `POST /api/v3/openai/moderations/pre` on `beforeRequestHook`
- Calls DeepKeep `POST /api/v3/openai/moderations/post` on `afterRequestHook`
- Blocks on `guardrail_action: block`
- Redacts or modifies request/response content on `redact` and `modify`
- Allows and logs `alert`

## Repo layout

- `plugins/deepkeep/manifest.json`
- `plugins/deepkeep/main.ts`
- `plugins/deepkeep/main.test.ts`
- `plugins/types.ts`
- `examples/portkey/guardrail-input.json`
- `examples/portkey/guardrail-output.json`
- `examples/portkey/config.json`

## DeepKeep config

Required credentials:

- `apiKey` or `bearerToken`

Required parameters:

- `apiBaseUrl`

Optional parameters:

- `firewallId`
- `inputFirewallId`
- `outputFirewallId`
- `chatId`
- `title`
- `timeoutMs`
- `failOpen`

## Portkey usage

Create separate guardrails for input and output, then attach them to a config:

```json
{
  "input_guardrails": ["guardrails-id-input"],
  "output_guardrails": ["guardrails-id-output"]
}
```

## Local checks

```bash
npm install
npm test
npm run typecheck
```

## Landing path

To get DeepKeep added as a Portkey partner guardrail, the code that usually lands upstream is the plugin package inside Portkey Gateway:

- `plugins/deepkeep/manifest.json`
- `plugins/deepkeep/main.ts`
- `plugins/deepkeep/main.test.ts`

That plugin can then be documented under Portkey's guardrail integrations and wired into the guardrail picker.

## Notes

- Portkey passes the last message text to guardrails.
- For streaming responses, output guardrails are informational only.
- This implementation is shaped to match Portkey's partner-guardrail plugin contract.
