# Integration Migration

## Status And Scope

All eight agreed integration `main` branches were imported using **non-squashed
git subtree imports**. Original commit IDs are preserved as ancestors. Source
repositories and public publishers remain unchanged. There has been **no publisher
cutover and no monorepo release**. GitHub release assets, issues, and pull requests
were not ported; Git tags are not a substitute for those GitHub records.

The public destination is live at
https://github.com/Deepkeepai/deepkeep-integrations. `main` and all 20 namespaced
source tags were pushed. On 2026-11-05 all eight directory URLs returned HTTP 200
without authentication, and the Open WebUI raw installation file was fetched
successfully. The [initial GitHub CI run](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42054023512)
passed every job, including the Agentgateway container build without publishing.

Upstream migration PRs, original-repository archival, and registry publisher
cutover are separate operations from creating this public destination. They have
not been performed as part of the source import.

`gilarel/pydantic-ai` is an upstream fork and is excluded. The actual
`Deepkeepai/pydantic-ai-deepkeep` package repository is included instead. No other
repositories are part of this migration.

## Imported Source Tips

These exact source SHAs were read from local remote-tracking refs with
`git for-each-ref --format="%(refname) %(objectname)" refs/remotes`.
They identify the imported source snapshot, not later monorepo edits or the
current state of a remote server.

| Source repository | Destination | Source ref | Imported SHA |
| --- | --- | --- | --- |
| [Deepkeepai/n8n-nodes-deepkeep](https://github.com/Deepkeepai/n8n-nodes-deepkeep) | `integrations/n8n` | `source-n8n/main` | `ba711303b21e336a06a8579f2fe321aef9edf4a1` |
| [Deepkeepai/agentgateway-deepkeep-webhook](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook) | `integrations/agentgateway` | `source-agentgateway/main` | `8c7506376b36aea62fd0111328855901005e6e2e` |
| [Deepkeepai/openwebui-deepkeep](https://github.com/Deepkeepai/openwebui-deepkeep) | `integrations/openwebui` | `source-openwebui/main` | `a706f97be218500375af0a33121c8a913492b81d` |
| [Deepkeepai/strands-deepkeep](https://github.com/Deepkeepai/strands-deepkeep) | `integrations/strands` | `source-strands/main` | `f0ed4e82f67ae48184f453f38045cc06f373d158` |
| [Deepkeepai/agno-deepkeep](https://github.com/Deepkeepai/agno-deepkeep) | `integrations/agno` | `source-agno/main` | `b01afdcc955f5368524c0a786fa5c8ab057b2049` |
| [Deepkeepai/crewai-tools-deepkeep](https://github.com/Deepkeepai/crewai-tools-deepkeep) | `integrations/crewai` | `source-crewai/main` | `9907b63f459490bc0461728d672e77dd4caa8ad8` |
| [Deepkeepai/deepkeep-kong-guardrail](https://github.com/Deepkeepai/deepkeep-kong-guardrail) | `integrations/kong` | `source-kong/main` | `26ee29dc0d49fe7f4942e30075a54f6b52545db4` |
| [Deepkeepai/pydantic-ai-deepkeep](https://github.com/Deepkeepai/pydantic-ai-deepkeep) | `integrations/pydantic-ai` | `source-pydantic-ai/main` | `0c1a52f1b6416e4973f5536268fb1dec9ff6375e` |

Historical commits still contain files at their original repository-root paths.
The subtree prefix exists in the import commits and subsequent monorepo tree;
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
runtime validation. n8n lint and build passed. `npm ci`
reported **24 vulnerabilities: 11 moderate, 11 high, and 2 critical** against the
untouched legacy lockfile. Moving source does not remediate those findings or
make dependencies safe. `npm audit --omit=dev` reported zero vulnerabilities;
the findings are in the development dependency graph. See [SECURITY.md](SECURITY.md).

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
edits do not update already published npm/PyPI artifacts.

The root `release.yml` workflow is manual-dispatch only, with no automatic
tag-push publishing. It is gated on repository variable
`MONOREPO_PUBLISHING_ENABLED` being exactly `true`; the variable is absent by
default, so publishing is disabled. Use `<integration>/v<VERSION>` tags and job
environments named `release-<integration>`. npm/PyPI publishing uses OIDC
trusted publishers. Registry trust and environment approval rules still require
configuration; environment names alone do not enforce approvals. Validation
requires the exact tag commit to be reachable from `main`, contain the monorepo
layout, and match the selected package version before testing and publishing.
The new repository variable `MONOREPO_PUBLISHING_ENABLED` was explicitly set to
`false` and verified after push. No registry tokens or trust bindings were migrated.

- [x] Import all eight `main` histories without squashing and namespace source tags.
- [x] Obtain explicit Agentgateway/Kong MIT approval and scan imported history.
- [x] Record local test/build baselines and outstanding n8n dependency findings.
- [x] Create the public destination, push main and source tags, and verify all
  eight directory URLs and the raw Open WebUI installation file anonymously.
- [ ] Finish exhaustive README-anchor and example-link validation before cutover.
- [x] Add root CI and validate workflow syntax and release-validator tests locally.
- [x] Verify all initial GitHub CI jobs, including the container build, pass.
- [ ] Coordinate and stop old publishers before enabling any new publisher;
  prevent concurrent or duplicate releases.
- [ ] Configure npm/PyPI OIDC trust for the exact repository, workflow, and
  `release-<integration>` environments; verify registry ownership and bindings.
- [ ] Configure any desired environment protection rules explicitly and verify
  GHCR package permissions while preserving the existing image endpoint.
- [ ] Validate the manual-dispatch workflow, tag/version checks, and independent
  package selection before setting `MONOREPO_PUBLISHING_ENABLED=true`.
- [ ] Obtain authorization for upstream changes, then follow the exact pending
  actions in [docs/REFERENCE_AUDIT.md](docs/REFERENCE_AUDIT.md).
- [ ] Publish only after cutover approval; verify artifacts, metadata, provenance,
  installation compatibility, and deployed upstream pages.
- [ ] Retain original repositories and raw installation files with relocation
  notices during transition. Seek separate approval before archiving anything.

## External Documentation

The [reference audit](docs/REFERENCE_AUDIT.md) preserves the verified official
sources and proposed replacements. No upstream migration PR has been submitted
as part of this migration. New Kong, CrewAI, or Pydantic AI listings would be
separate adoption proposals, not repairs to accepted upstream listings. Open
WebUI listing identity is unverified. Agno's live cookbook provenance must stay
intact. Recheck external status immediately before any authorized cutover.
