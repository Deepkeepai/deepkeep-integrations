# Integration Migration

## Status And Scope

Historically, all eight agreed integration `main` branches were imported using **non-squashed
git subtree imports**. Original commit IDs are preserved as ancestors. Source
repositories remain available. Agno's old publishing workflow is disabled;
Agentgateway's old CI now tests/builds without registry login or image pushes.
**All four Python metadata releases have now
been published and verified from this monorepo:** Strands 0.1.1, Agno 0.1.2,
CrewAI 0.1.3, and Pydantic AI 0.1.1. GitHub release assets, issues, and pull
requests were not ported; Git tags are not a substitute for those GitHub records.
Agentgateway image 0.1.0 and `latest` have also been published and verified from
the monorepo; [RELEASES.md](docs/RELEASES.md) records both image digests and evidence.

The public destination is live at
https://github.com/Deepkeepai/deepkeep-integrations. `main` and all 20 namespaced
source tags were pushed. On 2026-11-05 all eight directory URLs returned HTTP 200
without authentication, and the Open WebUI raw installation file was fetched
successfully. The [initial GitHub CI run](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42054023512)
passed every job, including the Agentgateway container build without publishing.

Upstream link-update PRs were submitted after the source import:
[Agentgateway #1475](https://github.com/agentgateway/website/pull/1475) merged on
2026-11-09; all four versioned guides were verified live with the monorepo link.
[Strands #5852](https://github.com/strands-agents/harness-sdk/pull/5852) is now
ready for maintainer review. The user supplied the exact human overview,
"The reason is housekeeping.", reviewed the two links, and authorized marking
it ready. Strands acceptance and live verification remain pending.
Five legacy repositories were subsequently archived after explicit approval;
[LEGACY_RETIREMENT.md](docs/LEGACY_RETIREMENT.md) records the batch and held repos. The
approved Python publisher cutovers are recorded in [RELEASES.md](docs/RELEASES.md).

n8n is permanently excluded from the monorepo at the user's request, not a paused
migration. Its canonical source is https://github.com/Deepkeepai/n8n-nodes-deepkeep.
The standalone repository is public and active, with `main` at
`ba711303b21e336a06a8579f2fe321aef9edf4a1`; its CI and Release workflows remain
active. No npm registry-trust migration is known and no monorepo npm release occurred.
The earlier user-reported email requesting a monorepo catalog URL is superseded
by this standalone destination. No counterrequest was sent; catalog follow-up and
live verification remain pending, with the last recorded link at the organization.

The current-tree boundary removes `integrations/n8n`, its root CI job, npm release
choice/job, and script enumeration through a normal forward deletion.
Older commits still contain n8n code. Preserve all imported
history and namespaced source tags: public PyPI/GHCR source-commit provenance is
immutable. Do not rewrite history, move tags, or change standalone repo settings.

[Release-preparation PR #1](https://github.com/Deepkeepai/deepkeep-integrations/pull/1)
was approved and merged on 2026-11-05, preparing unpublished Python metadata
patches on `main`: Strands 0.1.1, Agno 0.1.2,
CrewAI 0.1.3, and Pydantic AI 0.1.1. In separate Python 3.12.16 environments,
all 38 candidate integration tests and six release-validator tests passed;
all eight artifacts passed `twine check` and wheel metadata checks. The PR does
not create tags, publish packages, change registry bindings, or touch n8n.
Registry configuration, publisher cutover, tagging, and actual publication still
require separate approval per integration. After preparation, Strands alone was
explicitly approved, tagged, and published through run `42225772581`, with human
environment approval. Its fresh PyPI installation passed all 10 tests; both
artifact hashes and cryptographic PyPI publish attestations verified. The other
three releases were then separately authorized and published after CLI deployment
approvals explicitly requested by the owner. Their six artifacts verified and
fresh PyPI installations passed 28 tests, for 38 installed-wheel tests across all
four packages. Publishing was restored to disabled after validation.

Pending-work safety follow-up: Kong's four embedded functions now fail closed for
unsupported redaction/modification, unknown actions, and malformed responses.
Masking is disabled. All 382 policy/configuration tests passed in LuaJIT 2.1;
root CI now executes those tests. Licensed gateway HTTP/template enforcement is
still untested. Agentgateway now has read-only registry pre/postflight checks
and 19 mocked tests (25 root unit tests total). The owner granted package Actions
access, and approved run `42584070541` published image 0.1.0 after passing those
registry checks and 13 application tests. Separate read-only run `42585703883`
pulled the immutable digest and verified container startup and `/healthz` with
networking disabled. Live moderation and Kong gateway validation remain separate.

`gilarel/pydantic-ai` is an upstream fork and is excluded. The actual
`Deepkeepai/pydantic-ai-deepkeep` package repository is included instead. No other
repositories are part of this migration.

## Legacy Repository Notices

Notices are now live in all seven non-n8n legacy repositories in the agreed scope.
The six notice PRs are README-only; Agentgateway's notice was part of its
separate publisher cutover.
Default-branch READMEs were verified with the monorepo links. The Kong repository
remains private. These notice PRs did not change code, package names, release
references, raw installation URLs, visibility, or archival settings.

| Legacy repository | Notice | Status |
| --- | --- | --- |
| `pydantic-ai-deepkeep` | [PR #1](https://github.com/Deepkeepai/pydantic-ai-deepkeep/pull/1) | Merged 2026-11-10; main README verified with the `integrations/pydantic-ai` banner |
| `crewai-tools-deepkeep` | [PR #1](https://github.com/Deepkeepai/crewai-tools-deepkeep/pull/1) | Merged 2026-11-10; main README verified with the `integrations/crewai` banner and footer |
| `strands-deepkeep` | [PR #1](https://github.com/Deepkeepai/strands-deepkeep/pull/1) | Merged 2026-11-10; main README verified with the banner and accurate pending-catalog status |
| `agno-deepkeep` | [PR #1](https://github.com/Deepkeepai/agno-deepkeep/pull/1) | Merged 2026-11-10; main README verified with banner and separate cookbook/overview status; publisher still disabled |
| `openwebui-deepkeep` | [PR #1](https://github.com/Deepkeepai/openwebui-deepkeep/pull/1) | Merged 2026-11-11; public main notice verified; raw filter unchanged and v0.1.1 release link retained |
| `deepkeep-kong-guardrail` | [PR #1](https://github.com/Deepkeepai/deepkeep-kong-guardrail/pull/1) | Merged 2026-11-11; private main notice verified with historical-example and public-issue privacy warnings |
| `agentgateway-deepkeep-webhook` | [Cutover commit](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook/commit/c3bbe8d88fbd944f1498592c7725ed224c1dc16b) | Notice already live; legacy tests/builds active, image pushes off |

All non-n8n legacy notices in this scope are complete. Pydantic AI, CrewAI, Agno,
Open WebUI, and Kong are now archived read-only with preserved source heads and
visibility; Kong remains private. Historical Open WebUI release/raw URLs were
rechecked after archival and still work. Strands is held for catalog acceptance,
and Agentgateway archival needs a repository admin. No repositories were deleted;
n8n remains active standalone and LangChain stays separate. The company Cursor
integration is a separate new feature with a different license, not a retired import.

## Imported Source Tips

These exact source SHAs were read from local remote-tracking refs with
`git for-each-ref --format="%(refname) %(objectname)" refs/remotes`.
They identify the imported source snapshot, not later monorepo edits or the
current state of a remote server.

| Source repository | Historical import destination | Source ref | Imported SHA |
| --- | --- | --- | --- |
| [Deepkeepai/n8n-nodes-deepkeep](https://github.com/Deepkeepai/n8n-nodes-deepkeep) | `integrations/n8n` (removed from current-tree scope) | `source-n8n/main` | `ba711303b21e336a06a8579f2fe321aef9edf4a1` |
| [Deepkeepai/agentgateway-deepkeep-webhook](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook) | `integrations/agentgateway` | `source-agentgateway/main` | `8c7506376b36aea62fd0111328855901005e6e2e` |
| [Deepkeepai/openwebui-deepkeep](https://github.com/Deepkeepai/openwebui-deepkeep) | `integrations/openwebui` | `source-openwebui/main` | `a706f97be218500375af0a33121c8a913492b81d` |
| [Deepkeepai/strands-deepkeep](https://github.com/Deepkeepai/strands-deepkeep) | `integrations/strands` | `source-strands/main` | `f0ed4e82f67ae48184f453f38045cc06f373d158` |
| [Deepkeepai/agno-deepkeep](https://github.com/Deepkeepai/agno-deepkeep) | `integrations/agno` | `source-agno/main` | `b01afdcc955f5368524c0a786fa5c8ab057b2049` |
| [Deepkeepai/crewai-tools-deepkeep](https://github.com/Deepkeepai/crewai-tools-deepkeep) | `integrations/crewai` | `source-crewai/main` | `9907b63f459490bc0461728d672e77dd4caa8ad8` |
| [Deepkeepai/deepkeep-kong-guardrail](https://github.com/Deepkeepai/deepkeep-kong-guardrail) | `integrations/kong` | `source-kong/main` | `26ee29dc0d49fe7f4942e30075a54f6b52545db4` |
| [Deepkeepai/pydantic-ai-deepkeep](https://github.com/Deepkeepai/pydantic-ai-deepkeep) | `integrations/pydantic-ai` | `source-pydantic-ai/main` | `0c1a52f1b6416e4973f5536268fb1dec9ff6375e` |

Historical commits still contain files at their original repository-root paths.
The subtree prefix exists in the import commits and subsequent trees until removal;
history was not rewritten to prefix every original file. `git log --follow` is
not rewritten history and should not be assumed to cross every subtree merge.
Inspect the original source commit/path directly when tracing provenance:

```powershell
git log source-n8n/main -- README.md
git show ba711303b21e336a06a8579f2fe321aef9edf4a1:README.md
git log --all -- integrations/n8n/README.md
git for-each-ref --format="%(refname) %(objectname)" refs/tags
```

Imported tags are namespaced as `<integration>/v<VERSION>` to avoid collisions;
existing namespaced tags include n8n, Open WebUI, and Agno releases. They retain
the source history targets, not newly published monorepo artifacts. Not every
integration had source tags. Do not invent tags for untagged source releases.

## Public Suitability And Validation

Agentgateway and Kong MIT licensing was explicitly approved. Kong originated in
a private repository; its four commits were scanned clean by gitleaks. The full
imported history of 48 commits was also scanned with no leaks reported. These
results record the performed secret scans, not a guarantee that no secrets or
security flaws exist. Retain source notices and package-local licenses.

Recorded migration validation on Python 3.12: six pytest suites, all 63 tests
passing; all four Python packages built and their eight artifacts passed
`twine check`. Six release-validator tests and actionlint passed. Kong's two JSON
examples and one YAML example parsed successfully; that is not Kong schema or
runtime validation. In the 2026-11-05 imported n8n snapshot, lint and build passed. `npm ci`
reported **24 vulnerabilities: 11 moderate, 11 high, and 2 critical** against the
untouched legacy lockfile. Moving source does not remediate those findings or
make dependencies safe. `npm audit --omit=dev` reported zero vulnerabilities;
the findings were in that snapshot's development dependency graph, not the current
tree or a fresh standalone audit. See [SECURITY.md](SECURITY.md).

Root CI validates changed integrations, packaging, workflow syntax, and release
tooling, with a single aggregate `CI status` check. Python CI currently uses
3.12, not a complete supported-version matrix. The container build is delegated
to GitHub CI because the local Docker daemon was unavailable. Nested source
`.github/workflows` directories are retained for provenance and are inactive in
the current monorepo tree.

Historical tags still contain original root workflows. In particular, publishing
a GitHub Release against an imported Agno source tag can invoke its historical
publisher outside the new workflow's gate. **Do not backfill GitHub Releases on
imported source tags.** Do not add a repository-wide `PYPI_API_TOKEN` or trust the
historical `publish.yml` identity in this repository. Preserve tag targets rather
than rewriting history to remove these workflows.

## Publishing Contract And Gates

Keep package names, Python imports, independent versions, and the existing image
`ghcr.io/deepkeepai/agentgateway-deepkeep-webhook:latest` unchanged. Local metadata
edits do not update already published PyPI artifacts. n8n/npm publishing remains
exclusively standalone and is not a monorepo cutover target.

The root `release.yml` workflow is manual-dispatch only, with no automatic
tag-push publishing. It is gated on repository variable
`MONOREPO_PUBLISHING_ENABLED` being exactly `true`; the variable is absent by
default, so publishing is disabled. Use `<integration>/v<VERSION>` tags and job
environments named `release-<integration>` for the five publishable distributions
(four PyPI packages and Agentgateway's GHCR image). PyPI publishing uses OIDC
trusted publishers. GitHub approvals and the four PyPI paths are configured and
verified; future registry bindings still require explicit setup. Validation
requires the exact tag commit to be reachable from `main`, contain the monorepo
layout, and match the selected package version before testing and publishing.
The new repository variable `MONOREPO_PUBLISHING_ENABLED` was explicitly set to
`false` and verified after publishing. No long-lived registry tokens were copied;
new PyPI trusted publishers were configured by the owner.

Historically, six `release-<integration>` environments were configured and verified
with reviewer `gilarel` and a custom deployment policy allowing only branch
`main`. Self-review is allowed; this requires explicit approval but not a second
person. All four PyPI publishing paths are now demonstrated by successful,
attested publications. GHCR read/write publication and a separate read-only pull
are now verified for Agentgateway. The five in-scope job environments remain
unchanged. The empty `release-n8n` environment awaits inspection and possible
removal only after the main code changes merge; no deletion is claimed here.
See [PUBLISHING_CUTOVER.md](docs/PUBLISHING_CUTOVER.md) for exact binding fields,
the completed Python releases and remaining access requirements.

- [x] Import all eight `main` histories without squashing and namespace source tags.
- [x] Obtain explicit Agentgateway/Kong MIT approval and scan imported history.
- [x] Record historical local test/build baselines and imported-snapshot n8n dependency findings.
- [x] Create the public destination, push main and source tags, and verify all
  eight directory URLs and the raw Open WebUI installation file anonymously.
- [x] Audit the seven non-n8n integrations' Markdown files for relative links,
  anchors, and development paths; correct missing example dependencies/imports.
- [ ] Validate examples requiring live model/API calls or a licensed Kong runtime.
- [x] Add root CI and validate workflow syntax and release-validator tests locally.
- [x] Verify all initial GitHub CI jobs, including the container build, pass.
- [x] Coordinate the four Python releases and disable Agno's old publisher before
  cutover; tests were initially retained before approved archival. Agentgateway's
  image path was cut over separately and its old validation CI remains active.
- [x] Verify all four PyPI OIDC publishing paths through successful releases.
- [x] Set the permanent standalone n8n boundary; no monorepo npm publishing or trust setup.
- [x] Historically configure and verify six release environments with required reviewer
  `gilarel` and a `main`-only deployment policy.
- [x] Verify GHCR publication, matching version/latest digests, and a separate
  read-only image pull/runtime health check while preserving the image name.
- [x] Validate the manual-dispatch workflow, tag/version checks, and independent
  Python package selection; close the global gate after each approved batch.
- [x] Submit authorized Agentgateway and Strands link-update PRs; after the user
  provided their own overview and confirmed review, mark Strands ready.
- [x] Record the user's report that the n8n repository-URL email was sent.
- [ ] Follow up on the superseded n8n catalog request using the standalone URL;
  no counterrequest has been sent, and live verification remains pending.
- [ ] Obtain upstream acceptance and verify deployed pages as tracked in
  [docs/REFERENCE_AUDIT.md](docs/REFERENCE_AUDIT.md).
- [x] Publish the four Python packages after explicit approval and verify all
  artifacts, metadata, attestations, and isolated installations.
- [x] Complete the Agentgateway image-publisher cutover without stopping legacy tests/builds.
- [x] Verify the Open WebUI publisher's saved monorepo Repository link, unchanged
  filter/version, and valid historical v0.1.1 Release URL.
- [ ] Finish upstream PR acceptance and deployed documentation checks.
- [x] Retain original code, release references, and raw installation files while
  publishing the seven non-n8n legacy relocation notices.
- [x] Obtain explicit approval for the five-repository archival batch and verify
  archived flags, unchanged source/visibility, and historical Open WebUI downloads.
- [x] Open the [Agentgateway admin handoff](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook/issues/1)
  with verified cutover evidence and instructions to preserve the GHCR package.
- [ ] Obtain separate retirement approval for Strands after catalog acceptance
  and verify Agentgateway archival after its repository admin acts on the handoff.

## External Documentation

The [reference audit](docs/REFERENCE_AUDIT.md) preserves the verified official
sources, replacement URLs, and submitted migration PRs. New Kong, CrewAI, or Pydantic AI listings would be
separate adoption proposals, not repairs to accepted upstream listings. Open
WebUI's live listing now points to the monorepo and its embedded code matches;
its historical v0.1.1 release link remains unchanged and valid. Agno's cookbook provenance must stay
intact. Recheck external status immediately before any authorized cutover.
