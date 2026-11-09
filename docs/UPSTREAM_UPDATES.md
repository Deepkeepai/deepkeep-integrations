# Upstream Link Updates

The GitHub submissions below were opened on 2026-11-05. Agentgateway subsequently
merged, and all four published guide versions were verified with the new source
link; Strands is still awaiting review. Replacement directory URLs returned
HTTP 200 before submission. Source repositories remain available. The four Python
metadata releases and Agentgateway image 0.1.0 are now verified. Agno's old
publisher is disabled, and Agentgateway's legacy CI builds/tests without pushing.
See [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) for acceptance evidence and caveats.

| Update | Submission | Status / next action |
| --- | --- | --- |
| Agentgateway | [website #1475](https://github.com/agentgateway/website/pull/1475) | Merged 2026-11-09; all four live guides verified with the new link and unchanged image name |
| Strands | [harness-sdk #5852](https://github.com/strands-agents/harness-sdk/pull/5852) | Ready for maintainer review; user-authored overview and link review completed |
| Open WebUI | [Existing listing](https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e) | Repository URL updated by publisher and publicly verified; retain historical v0.1.1 release URL |
| n8n | Deferred | Skipped at the user's request; no portal, package, or repository changes |

The remaining specifications and request text are retained for review and follow-up.
Legacy source-repository notice PRs for Pydantic AI and CrewAI are tracked in
[MIGRATION.md](../MIGRATION.md#legacy-repository-notices); they are distinct from
official framework documentation submissions.

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

Strands requires a Human Overview written by the human author, not an AI agent.
The user supplied "The reason is housekeeping.", confirmed review of the two
URL changes, and explicitly authorized marking the PR ready. Those two human
checklist items are now checked; the unrun `hatch run prepare` item is not.
Its description documents the original metadata mismatch and now links to the
verified Strands 0.1.1 release, whose published URLs and attestations identify the
monorepo. The old bot comment may remain until upstream rechecks; maintainer
acceptance and deployment verification are still pending.

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
On 2026-11-05 the portal redirected to a sign-in page. GitHub authentication does
not provide access to this separate account, and no catalog change was submitted.

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

- Open WebUI: [the live listing](https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e)
  now points to the monorepo directory. The saved edit was verified through its
  official API. Embedded code remains 0.1.1 and matches the migrated source; its
  historical release URL stays unchanged and valid. [Details](../integrations/openwebui/COMMUNITY_LISTING.md)
  are recorded; no further listing change is needed for this migration.
- Agno: retain the official cookbook source link. No stale vendor repository link
  was found in the live example, so there is no mandatory replacement PR.
- CrewAI: maintain vendor-hosted instructions as requested by maintainers; no
  accepted DeepKeep page exists to update.
- Kong: published schemas confirm `block_detail` for 3.14-3.16. The current
  examples fail closed rather than claim unsupported masking. A new proposal
  still needs licensed gateway HTTP/template enforcement tests.
- Pydantic AI: a renewed listing proposal requires maintainer consultation and
  community-adoption work, not a mechanical URL replacement.
