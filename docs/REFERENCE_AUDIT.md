# Integration Reference Audit

Original research audit: **2026-11-05**, from
`INTEGRATIONS_MIGRATION_REFERENCES.md` in the parent workspace. This tracker
preserves its verified findings and exact source/replacement links. External
statuses below are audit-time observations, not newly revalidated claims.

All eight integrations have since been imported locally with history; see
[MIGRATION.md](../MIGRATION.md) for source SHAs, licensing, validation, and gates.
Original source repositories and public publishers remain unchanged. No publisher
cutover, monorepo release, upstream migration PR, or source archive has occurred.
GitHub release assets, issues, and PRs were not ported. Upstream PRs and original
repository archival are not authorized yet.

The proposed public destination is `Deepkeepai/deepkeep-integrations`. It returned
HTTP 404 during the original research audit. That is a historical observation,
not a fresh availability check. Do not replace external links until the exact
destination pages/files work anonymously. Proposed links below are not claims of
completed or deployed replacements. "Not verified" does not mean proven absent.

## Official Reference Tracker

| Integration | Verified official exposure | Pending action |
| --- | --- | --- |
| n8n | Verified live catalog; GitHub link points to the organization | Request integration-specific destination through existing Creator Portal record/catalog maintainers; review legacy operations text |
| Agentgateway | Four live versioned guides link to old repo and existing image | Future PR after authorization to `agentgateway/website` replacing four direct repository links; preserve image |
| Open WebUI | Vendor listing draft; no live community listing verified | Locate listing ID/owner or record as unpublished; update raw install URL and vendor guide |
| Strands | Live partner catalog links to old repo and README | Future PR after authorization updating `github` and `docsUrl` in existing YAML |
| Agno | Live official cookbook/example; separate overview proposal pending | Preserve cookbook links; optional external integration link through docs workflow |
| CrewAI | Docs submissions closed unmerged; vendor-hosted docs requested | Maintain vendor guide; no accepted upstream page to replace |
| Kong | Generic custom-guardrail docs, not a DeepKeep listing | Optional new, version-appropriate proposal; not a link migration |
| Pydantic AI | Third-party page has no DeepKeep entry; proposal closed unmerged | Maintain vendor guide; consult maintainers before renewed proposal |

## n8n

- Live catalog: https://n8n.io/integrations/deepkeep/
- The page explicitly describes DeepKeep as verified by n8n. Its current GitHub
  destination is https://github.com/Deepkeepai/, not the standalone repository.
- Catalog operations describe legacy Firewall Conversation behavior; compare
  with current v2 moderation before requesting copy changes.
- Update mechanism: https://creators.n8n.io/nodes through the existing record or
  catalog maintainers. Self-service editing was not verified and no public source
  for this specific record was identified.
- Submission guidance: https://docs.n8n.io/integrations/community-nodes/installation/verified-install/
  and https://docs.n8n.io/connect/create-nodes/deploy-your-node/submit-community-nodes.md
- No DeepKeep-specific source was found in the bounded `n8n-io/n8n-docs` search.
- Proposed catalog destination: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/n8n

https://registry.npmjs.org/n8n-nodes-deepkeep/latest reported `0.2.9` with old
repository/issue URLs. A future release should use the new Git repository for
`repository.url`, `integrations/n8n` for `repository.directory`, and the new issues
URL for `bugs.url`. Preserve `n8n-nodes-deepkeep` and configure trusted publishing/
provenance before cutover. Local metadata edits do not update published metadata.
After a catalog change, re-fetch the rendered destination and operations text.

## Agentgateway

Verified live guides:

- https://agentgateway.dev/docs/standalone/latest/integrations/llm/guardrails/deepkeep/
- https://agentgateway.dev/docs/standalone/main/integrations/llm/guardrails/deepkeep/
- https://agentgateway.dev/docs/standalone/1.6.x/integrations/llm/guardrails/deepkeep/
- https://agentgateway.dev/docs/standalone/1.5.x/integrations/llm/guardrails/deepkeep/

Each references the standalone repository and
`ghcr.io/deepkeepai/agentgateway-deepkeep-webhook:latest`. The correct upstream
source is `agentgateway/website`, not the runtime repository. Paths on `main`:

```text
content/docs/standalone/latest/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/main/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/1.6.x/integrations/llm/guardrails/deepkeep.md
content/docs/standalone/1.5.x/integrations/llm/guardrails/deepkeep.md
```

- Exact example source: https://github.com/agentgateway/website/blob/main/content/docs/standalone/latest/integrations/llm/guardrails/deepkeep.md
- Proposed direct repository replacement: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/agentgateway
- Preserve the GHCR endpoint; confirm its package permissions before publishing
  moves. Keep internal `overview.md`/`webhooks.md` navigation intact.
- Accepted PRs: https://github.com/agentgateway/website/pull/935,
  https://github.com/agentgateway/website/pull/982,
  https://github.com/agentgateway/website/pull/1001
- https://github.com/agentgateway/agentgateway/issues/3224 was closed in favor of
  the webhook extension, not a shipped native provider.

After an authorized PR merges, verify all four deployed versions and check for
additional versions introduced before cutover.

## Open WebUI

- Vendor document explicitly marked draft: https://github.com/Deepkeepai/openwebui-deepkeep/blob/main/COMMUNITY_LISTING.md
- Current raw installation file: https://raw.githubusercontent.com/Deepkeepai/openwebui-deepkeep/main/deepkeep_openwebui_filter.py
- Proposed repository destination: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/openwebui
- Proposed raw installation URL: https://raw.githubusercontent.com/Deepkeepai/deepkeep-integrations/main/integrations/openwebui/deepkeep_openwebui_filter.py
- Generic official functions source: https://github.com/open-webui/docs/blob/main/docs/features/extensibility/plugin/functions/index.mdx
- No DeepKeep-specific official docs file or community listing ID was verified.
  https://openwebui.com/search?query=deepkeep returned a client-rendered shell,
  not auditable listing results.

Locate the actual listing URL and owner before claiming an update. If none exists,
record it as unpublished. Use the raw Python file, not a directory URL, for
URL-based installation. Keep the old raw file usable during transition. Imported
function copies do not automatically update when source/listing URLs change.

## Strands

- Verified live catalog: https://strandsagents.com/integrations/
- Authoritative source: https://github.com/strands-agents/harness-sdk/blob/main/site/src/content/catalog/strands-deepkeep.yaml
- Acceptance: https://github.com/strands-agents/harness-sdk/pull/3996 merged 2026-09-21.
- Contribution guidance: https://strandsagents.com/docs/integrations/get-featured/
- Current `github`: https://github.com/Deepkeepai/strands-deepkeep
- Current `docsUrl`: https://github.com/Deepkeepai/strands-deepkeep#readme
- Proposed `github`: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands
- Proposed `docsUrl`: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/strands#readme

Use the existing YAML record, not a duplicate listing. Preserve package
`strands-deepkeep` and its generated PyPI link. Do not manually edit bot-maintained
`catalog-stats.json` as the link source. Verify the rendered catalog after merge.
https://pypi.org/pypi/strands-deepkeep/json confirmed `0.1.0` and old-repo links in
metadata/description; update through a future release. Vendor notes still saying
"Submit" are stale, not evidence that the accepted listing is pending.

## Agno

- Verified live example: https://docs.agno.com/examples/agents/guardrails/deepkeep-ai-firewall
- Cookbook source: https://github.com/agno-agi/agno/blob/main/cookbook/02_agents/08_guardrails/deepkeep_ai_firewall.py
- Docs source: https://github.com/agno-agi/docs/blob/main/examples/agents/guardrails/deepkeep-ai-firewall.mdx
- Cookbook acceptance: https://github.com/agno-agi/agno/pull/9784 merged 2026-08-26.
- Separate overview proposal: https://github.com/agno-agi/docs/pull/760 was open,
  unmerged, and not draft at audit time.
- Live overview https://docs.agno.com/guardrails/overview did not contain that
  proposed catalog table.

The live example installs `agno-deepkeep`, imports `agno_deepkeep`, and links to
Agno's cookbook. No stale standalone DeepKeep repo link was found there. Do not
replace Agno-owned source links. An optional additional external link may target
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/agno.
Coordinate with https://github.com/agno-agi/docs/blob/main/scripts/README.md.
The live page differs from current source MDX; verify source and deployment
separately and track #760 independently of migration.

https://pypi.org/pypi/agno-deepkeep/json confirmed `0.1.1` with only a vendor
homepage in project URLs. Add integration-specific repository/docs metadata in a
future release while preserving package identity and coordinating trusted publishing.

## CrewAI

No official DeepKeep page was verified. Candidate URLs returned generic home
content; organization code search found no DeepKeep entry.

- https://github.com/crewAIInc/crewAI/pull/5536: closed unmerged, older built-in tools proposal.
- https://github.com/crewAIInc/crewAI/pull/7089: closed unmerged, docs proposal.
- https://github.com/crewAIInc/crewAI/pull/7202: closed unmerged, replacement docs proposal.
- Maintainer direction: https://github.com/crewAIInc/crewAI/pull/7202#issuecomment-5508136001
  asks for usage docs in the DeepKeep package repository.

The proposed `docs/edge/en/learn/deepkeep-guardrails.mdx` was not on upstream
`main`. Do not represent it as accepted or submit an automatic URL-replacement PR.
Maintain the vendor guide at
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/crewai.
Seek agreement before renewed listing work.
https://pypi.org/pypi/crewai-tools-deepkeep/json confirmed `0.1.2` with old repo
metadata/description. Update in a future release, preserving distribution
`crewai-tools-deepkeep` and import `crewai_deepkeep`.

## Kong

Verified generic official pages, neither a DeepKeep listing:

- https://developer.konghq.com/plugins/ai-custom-guardrail/
- https://developer.konghq.com/ai-gateway/policies/ai-custom-guardrail/

Potential sources in `Kong/developer.konghq.com`:

```text
app/_kong_plugins/ai-custom-guardrail/index.md
app/_kong_plugins/ai-custom-guardrail/examples/
app/_ai_gateway_policies/ai-custom-guardrail/index.md
```

Bounded searches found no DeepKeep code/PR match. Vendor
`examples/kong-docs-submission.md` is proposal material, not an accepted listing.
Any upstream change is a new submission. Distinguish legacy plugins from AI Gateway
2.0 policies and reconcile proposal `block_detail` with official `block_details`
before proposing examples. Proposed guide:
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/kong

The original audit required review before exposing this private source. Subsequent
migration validation recorded explicit MIT approval and a clean gitleaks scan of
all four Kong commits, plus the full imported history. This does not authorize
upstream submissions or certify runtime/dependency safety.

## Pydantic AI

- Official third-party page: https://pydantic.dev/docs/ai/capabilities/third-party/
- Source: https://github.com/pydantic/pydantic-ai/blob/main/docs/capabilities/third-party.md
- Neither contained a DeepKeep entry during the audit.
- https://github.com/pydantic/pydantic-ai/pull/7778 is closed **unmerged**, not accepted.
- Maintainer response: https://github.com/pydantic/pydantic-ai/pull/7778#issuecomment-5439420917
  asks for community sharing/adoption first.
- Old repo link on contributor branch: https://github.com/gilarel/pydantic-ai/blob/docs/deepkeep-third-party-capability/docs/capabilities/third-party.md

Updating that fork does not update official docs. The fork is excluded from this
migration; the actual `pydantic-ai-deepkeep` package source is included. Consult
maintainers before a new proposal and use current page structure, not outdated
insertion context. Proposed vendor guide:
https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/pydantic-ai

https://pypi.org/pypi/pydantic-ai-deepkeep/json confirmed `0.1.0`, with Repository
and Documentation pointing to the standalone repo. Update in a future release
without changing package or import names.

## Cutover Tracking

All external replacement actions remain pending destination validation and
authorization. See [MIGRATION.md](../MIGRATION.md) for publishing gates. Preserve
old repositories/install files through compatibility validation; archive only
with separate authorization. New Kong, CrewAI, and Pydantic AI listings are
separate adoption work, not mandatory migrations of accepted entries.

For each authorized submission, record submission URL, owner, submitted date,
merged date, live verification date, and remaining old links. No migration
submission URLs exist yet. Verify rendered pages after deployment, not merely PR
merge. Never count pending upstream action as completed documentation migration.

## Audit Limits

Searches were bounded and mainly indexed default branches, not all history or
private catalogs. Negative findings mean not found in that scope. Rendered pages
were checked independently where accessible. A combined GitHub code search failed
with HTTP 422 and was replaced with scoped queries; later HTTP 403 rate limiting
blocked a follow-up n8n lookup. No authenticated n8n Creator Portal or Open WebUI
community inspection was performed. Open WebUI search was client-rendered. The
Agno source/live discrepancy remains unexplained.

The original research did not install packages, pull containers, run runtime
tests, or inspect deployment pipelines. Later local migration tests/builds and
secret scans are recorded separately in [MIGRATION.md](../MIGRATION.md); they do
not retroactively validate external references or publisher configuration.
Revalidate external pages and PR status immediately before cutover.
