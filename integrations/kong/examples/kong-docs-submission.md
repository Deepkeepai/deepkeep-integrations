# Kong docs submission notes

Status: Proposal only, not accepted by Kong.

Lakera's docs PR followed this pattern:

- add the plugin page under `app/_kong_plugins/<plugin-name>/`
- add example pages
- add audit-log reference entries
- add the landing-page card for AI Gateway

For DeepKeep, the docs PR should include:

1. `AI Custom Guardrail` example content for pre and post moderation.
2. Audit log fields for `block_reason`, `block_detail`, and `masked`.
3. A short how-to showing DeepKeep request and response moderation.
4. The landing-page card under the guardrails section.

Keep [integrations/kong](https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/kong) as the source of truth for the Kong payloads and DeepKeep request/response mapping. The singular `block_detail` metric matches Kong's published schemas for 3.14, 3.15, and 3.16; do not rename it based only on the overview's plural wording.

Before submission, test the examples on the intended licensed Kong deployment.
The functions supply no replacement text: masking is disabled, `masked` is always
false, and redaction/modification actions block conservatively. Local LuaJIT tests
do not verify gateway enforcement or content replacement on licensed Kong.
