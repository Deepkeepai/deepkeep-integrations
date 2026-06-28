# Kong docs submission notes

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

Keep the public integration repo as the source of truth for the Kong payloads and DeepKeep request/response mapping.
