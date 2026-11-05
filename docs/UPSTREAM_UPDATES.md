# Prepared Upstream Link Updates

These are submission-ready change specifications, not submitted pull requests.
Validate the destination URLs and obtain upstream-change approval before sending.
See [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) for acceptance evidence and caveats.

## Agentgateway Website

Repository: `agentgateway/website`; base branch: `main`.

Suggested title: `docs: point DeepKeep adapter links to integrations monorepo`

In each of these files, replace only
`https://github.com/Deepkeepai/agentgateway-deepkeep-webhook` with
`https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/agentgateway`:

```text
content/docs/standalone/latest/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/main/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/1.6.x/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/1.5.x/integrations/llm/guardrails/deepkeep.md
```

Recheck for newly added versions at submission time. Preserve internal guide
navigation and `ghcr.io/deepkeepai/agentgateway-deepkeep-webhook:latest`.

Suggested PR body:

```text
DeepKeep's webhook adapter source is now also available in its public integrations
monorepo. Update the repository links across the existing versioned guides to the
adapter's exact directory. The image name, webhook routes, configuration, and
examples are unchanged. The original repository remains accessible during the
migration.

Validation: the replacement directory and README are publicly accessible.
No runtime or container configuration changes are included.
```

Only include the validation statement after performing that check. After merge,
verify all affected rendered guide versions.

## Strands Catalog

Repository: `strands-agents/harness-sdk`; base branch: `main`.
File: `site/src/content/catalog/strands-deepkeep.yaml`.

Suggested title: `docs: update DeepKeep catalog repository and guide links`

Replace the existing two fields without adding a second catalog record:

```yaml
github: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands
docsUrl: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands#readme
```

Keep the `strands-deepkeep` package field, partner classification, dates, and
other metadata unchanged. Do not edit generated popularity statistics.

Suggested PR body:

```text
Update the existing DeepKeep partner integration's source and documentation links
to its directory in DeepKeep's public integrations monorepo. The PyPI package
name, Python imports, and integration behavior are unchanged. The original
repository remains accessible during migration.

Validation: the integration directory and README are publicly accessible.
```

After merge, verify both links on https://strandsagents.com/integrations/.

## n8n Catalog Request

Use the existing Creator Portal record or contact catalog maintainers; the
specific public catalog record was not found in `n8n-io/n8n-docs`.

```text
Please update DeepKeep's GitHub resource link on
https://n8n.io/integrations/deepkeep/ to:
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/n8n

The verified npm package remains n8n-nodes-deepkeep. Its package name and node
identity are not changing. Please also review the operation descriptions against
the current package, since the page currently describes legacy Firewall
Conversation operations.
```

Coordinate any package verification or trusted-publisher requirements separately
before releasing from the monorepo. Do not create a duplicate verified-node record.

## Other Integrations

- Open WebUI: locate the actual community listing ID and owner before proposing
  an edit. The new raw filter URL is documented in the integration's listing draft.
- Agno: retain the official cookbook source link. No stale vendor repository link
  was found in the live example, so there is no mandatory replacement PR.
- CrewAI: maintain vendor-hosted instructions as requested by maintainers; no
  accepted DeepKeep page exists to update.
- Kong: a new integration example proposal requires target-version schema review.
- Pydantic AI: a renewed listing proposal requires maintainer consultation and
  community-adoption work, not a mechanical URL replacement.
