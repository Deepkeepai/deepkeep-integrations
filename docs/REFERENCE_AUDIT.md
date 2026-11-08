# Integration Reference Audit

Original research audit: **2026-11-05**, from
`INTEGRATIONS_MIGRATION_REFERENCES.md` in the parent workspace. This tracker
preserves its verified findings and exact source/replacement links. External
statuses below are audit-time observations, not newly revalidated claims.

All eight integrations have since been imported locally with history; see
[MIGRATION.md](../MIGRATION.md) for source SHAs, licensing, validation, and gates.
Original repositories and their workflows remain unchanged. Strands 0.1.1 is now
published and verified from the monorepo; no source archive has occurred. GitHub release assets,
issues, and PRs were not ported. Authorized migration submissions are now tracked
below; original-repository archival remains a separate, unperformed operation.

The public destination `Deepkeepai/deepkeep-integrations` was created and pushed
on 2026-11-05. All eight integration directory URLs returned HTTP 200 anonymously,
and the Open WebUI raw file was fetched successfully. These are now available
replacement destinations, not claims that upstream sites have updated their links.
"Not verified" does not mean proven absent.

## Official Reference Tracker

| Integration | Verified official exposure | Pending action |
| --- | --- | --- |
| n8n | Verified live catalog; GitHub link points to the organization | Deferred at the user's request; leave this integration and its catalog unchanged |
| Agentgateway | Four live versioned guides link to old repo and existing image | [website #1475](https://github.com/agentgateway/website/pull/1475) open; four URL replacements, image unchanged |
| Open WebUI | [Live function listing](https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e) verified through official public API | Publisher must edit its repository link; embedded filter matches migrated source |
| Strands | Live partner catalog links to old repo and README | [harness-sdk #5852](https://github.com/strands-agents/harness-sdk/pull/5852) draft; Human Overview and human review required |
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

Follow-up on 2026-11-05: the Creator Portal requires a separate sign-in. No
authenticated portal session is available, so no n8n update was submitted. The
existing record owner must submit the prepared request in [UPSTREAM_UPDATES.md](UPSTREAM_UPDATES.md).

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

Migration PR [#1475](https://github.com/agentgateway/website/pull/1475) was submitted
by `gilarel` on 2026-11-05 after checking the current source and replacement URL.
It changes only the four direct links; the image and examples are untouched.
The author explicitly approved DCO certification, the PR commit was signed off,
and the DCO check passed.
Merge and live deployment verification remain pending. After merge, verify all
four deployed versions and check for additional versions introduced before cutover.

## Open WebUI

- Vendor document explicitly marked draft: https://github.com/Deepkeepai/openwebui-deepkeep/blob/main/COMMUNITY_LISTING.md
- Current raw installation file: https://raw.githubusercontent.com/Deepkeepai/openwebui-deepkeep/main/deepkeep_openwebui_filter.py
- Proposed repository destination: https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/openwebui
- Proposed raw installation URL: https://raw.githubusercontent.com/Deepkeepai/deepkeep-integrations/main/integrations/openwebui/deepkeep_openwebui_filter.py
- Generic official functions source: https://github.com/open-webui/docs/blob/main/docs/features/extensibility/plugin/functions/index.mdx
- The initial HTML-only search returned a client-rendered shell. A follow-up
  through the official public search API resolved the listing:
  https://api.openwebui.com/api/v1/posts/search?query=deepkeep&sort=top&t=all&page=1
- Verified live listing: https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e
- Publisher account: `@gilharel11159626bf`; authorized edit access is still required.
- Edit page: https://openwebui.com/posts/11544def-a732-4f5a-bb04-8df2e9fedd7e/edit

The public listing's embedded 0.1.1 filter was compared with the monorepo source
and matches after newline normalization. Only its repository description needs a
migration edit. Keep its historical old-repository `v0.1.1` release link valid;
there is no replacement monorepo release. Prepared instructions are in
[COMMUNITY_LISTING.md](../integrations/openwebui/COMMUNITY_LISTING.md).
No site update was submitted. Use the raw Python file for URL-based installation;
already imported function copies do not automatically update with listing links.

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

Migration PR [#5852](https://github.com/strands-agents/harness-sdk/pull/5852) was
submitted by `gilarel` on 2026-11-05 as a draft at the author's request. It changes
only `github` and `docsUrl`; YAML parsing and a comparison of all other fields
passed. The upstream template requires the human author's own Human Overview,
which is intentionally unfilled. Human review, ready-for-review status, merge,
and live catalog verification remain pending.

Follow-up: the catalog bot flagged the published PyPI metadata still pointing to
the old repository. The draft description now provides migration/source-commit
evidence and explicitly acknowledges that registry metadata has not changed.
This advisory does not block merging by itself; package ownership remains for
reviewer verification. A new package release is needed to change published URLs.

Release follow-up: Strands 0.1.1 was published from the new repository and its
Repository/Documentation metadata now matches the proposed catalog entry. Both
publish attestations verified cryptographically, and a fresh PyPI installation
passed all 10 tests. See [RELEASES.md](RELEASES.md) and the updated draft PR
description. The original bot comment is historical; no claim is made that an
upstream reviewer has rechecked it or accepted the catalog change.

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
2.0 policies. Follow-up schema inspection resolved the metric spelling concern:
the published 3.14, 3.15, and 3.16 JSON schemas define singular `block_detail`,
despite the overview prose saying `block_details`. Keep the example key unchanged.
Twelve focused static checks passed across four configurations and three schemas;
that is not full Kong runtime validation. The examples do not supply replacement
text, so redaction/modification enforcement remains unverified and must not be
claimed as working. Proposed guide:
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

The destination directories and raw filter URL are verified. Agentgateway and
Strands submissions are open, with Strands intentionally a draft. n8n remains
blocked on the existing Creator Portal account. Prepared request text and exact
changes are in [UPSTREAM_UPDATES.md](UPSTREAM_UPDATES.md).
See [MIGRATION.md](../MIGRATION.md) for publishing gates. Preserve
old repositories/install files through compatibility validation; archive only
with separate authorization. New Kong, CrewAI, and Pydantic AI listings are
separate adoption work, not mandatory migrations of accepted entries.

| Integration | Submission / owner | Submitted | Merged | Live verified |
| --- | --- | --- | --- | --- |
| Agentgateway | [#1475](https://github.com/agentgateway/website/pull/1475), gilarel | 2026-11-05 | Pending | Pending |
| Strands | [#5852](https://github.com/strands-agents/harness-sdk/pull/5852), gilarel | 2026-11-05, draft | Pending | Pending |
| n8n | Existing portal account owner needed | Not submitted | Not applicable | Pending |

The old links remain in upstream default branches until acceptance. Verify
rendered pages after deployment, not merely PR merge. Never count pending
upstream action as completed documentation migration.

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
