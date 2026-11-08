# Publishing Cutover

Initial audit: 2026-11-05. Strands 0.1.1 was subsequently published and verified
on 2026-11-08; see [RELEASES.md](RELEASES.md). No other packages or container
images have been published here, and no original workflow has been disabled.

## Verified State

- `MONOREPO_PUBLISHING_ENABLED` is explicitly `false`.
- All six publishable integrations still match their imported source `main` SHAs.
- Six GitHub environments exist, each requiring reviewer `gilarel` and allowing
  deployments only from branch `main`: `release-n8n`, `release-agentgateway`,
  `release-strands`, `release-agno`, `release-crewai`, `release-pydantic-ai`.
- Self-review is allowed, so the author can explicitly approve a manually
  dispatched release. This is an approval gate, not two-person separation of duty.
  Repository administrators can change protection settings; do not treat names
  or reviewer configuration as immutable security boundaries.
- No repository Actions secrets were copied. npm/PyPI publication uses OIDC;
  Agentgateway uses GitHub's automatically supplied `GITHUB_TOKEN`.
- Strands release run `42225772581` succeeded after human environment approval.
  That verifies its publishing path, not the other packages' bindings. Successful
  CI by itself is not proof of registry publishing authorization.

## Registry Bindings To Configure

These are required settings. Strands' exact binding has been demonstrated by
its successful attested publication; other bindings still need verification.
Use existing npm/PyPI projects, not differently named replacement packages.

| Field | Value |
| --- | --- |
| Provider | GitHub Actions |
| Owner / organization | `Deepkeepai` |
| Repository | `deepkeep-integrations` |
| Workflow filename | `release.yml` |
| Workflow path, for reference | `.github/workflows/release.yml` |

The registry form takes the filename, not the display name `Release Integration`.
Select the exact package-specific environment:

| Registry | Existing package | Environment | Recorded published version |
| --- | --- | --- | --- |
| npm | `n8n-nodes-deepkeep` | `release-n8n` | `0.2.9` |
| PyPI | `strands-deepkeep` | `release-strands` | `0.1.1`, verified publication |
| PyPI | `agno-deepkeep` | `release-agno` | `0.1.1` |
| PyPI | `crewai-tools-deepkeep` | `release-crewai` | `0.1.2` |
| PyPI | `pydantic-ai-deepkeep` | `release-pydantic-ai` | `0.1.0` |

For npm, use the existing package's **Settings > Trusted Publishers** and permit
the workflow's direct `npm publish` operation, not only staged publishing. The
workflow uses `--provenance`; trusted publishing requires a supported npm CLI
(at least 11.5.1). Node 24 is selected by the workflow.

For PyPI, use each existing project's **Publishing** settings and add a GitHub
trusted publisher with the fields above. Keep the environment restriction rather
than granting an unrestricted workflow identity. Do not introduce a shared
`PYPI_API_TOKEN` to bypass trust configuration.

References: [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)
and [PyPI publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).

The local `npm whoami` check returned HTTP 401. This means no usable local npm
session was available; it does **not** prove that GitHub OIDC publishing would
fail. Registry settings require the appropriate project-owner account and have
not been inspected through an authenticated registry management session.

## Agentgateway Container Access

Keep `ghcr.io/deepkeepai/agentgateway-deepkeep-webhook` unchanged. Its publishing
job uses environment `release-agentgateway` and `GITHUB_TOKEN` with `packages: write`.

In the existing container package's GitHub settings, verify the new repository
has Actions write access. Repository admin access alone does not prove access to
an existing package. Changing source repositories does not transfer package access.

The current CLI token lacks `read:packages`; the package API returned HTTP 403.
Package association, inherited permissions, visibility, and current image digests
therefore remain unverified. Granting a token scope requires the account owner's
approval; no authentication scopes were changed during this audit.

## Coordinate Existing Publishers

| Integration | Existing publication path | Cutover requirement |
| --- | --- | --- |
| n8n | Active `release.yml`, triggered by `v*.*.*` tag pushes, npm OIDC/provenance | Coordinate and stop the old release publisher before the new publisher is enabled |
| Agentgateway | Active `ci.yml`, pushes images on source `main` updates | Stop old image pushes while retaining tests if desired; otherwise the old repository can overwrite `latest` |
| Agno | Active `publish.yml`, triggered by GitHub Release publication, using `PYPI_API_TOKEN` | Coordinate stopping that publisher and moving to OIDC; do not copy its token |
| Strands | No repository-defined publisher found | Identify the existing package owner and any manual/external upload process |
| CrewAI | No repository-defined publisher found | Identify the existing package owner and any manual/external upload process |
| Pydantic AI | No repository-defined publisher found | Identify the existing package owner and any manual/external upload process |

Absence of a checked-in workflow does not prove there is no publisher. Original
repositories remain authoritative for releases until an explicit cutover. Do not
disable unrelated workflows or archive repositories as a side effect.

## Prepare Fresh Versions

The imported npm/PyPI package versions matched already published versions.
[Python patch candidates](PYTHON_RELEASE_CANDIDATES.md) now prepare fresh versions
for the four Python packages; these are not publications. Do not use republishing
as a permission test. Prepare a reviewed version
bump in the selected integration, including the n8n lockfile where appropriate,
and rerun its tests/build/artifact checks before creating a new monorepo tag.

The release validator checks tag/package agreement and monorepo layout, not
whether that version is still unused in a registry. Recheck registry availability
immediately before release. Tags are immutable release references; do not move
an imported historical tag or reuse an existing package version.

For Agentgateway, select a new immutable image version and verify it is unused.
The release also moves `latest`, so obtain explicit rollout approval first.

## Execute Only After Approval

1. Confirm the selected integration's source snapshot, package ownership, new
   version, tests, and exact new trust binding or GHCR permission.
2. Coordinate the old publishing path and confirm it cannot publish concurrently.
3. Confirm the protected environment reviewer and `main` branch policy still exist.
4. Merge the reviewed version bump to `main`; create and push the new tag
   `<integration>/vMAJOR.MINOR.PATCH` at that monorepo commit.
5. Only after explicit release approval, enable `MONOREPO_PUBLISHING_ENABLED`,
   dispatch `Release Integration` on branch `main` with the selected integration
   and exact tag, then review the waiting environment deployment.
6. Verify package contents, registry metadata, installation, provenance where
   available, and container digest. Disable publishing again if the cutover is
   being staged rather than permanently completed.
7. Recheck upstream documentation and catalog destinations after acceptance.
   Keep old repositories/raw files accessible during compatibility validation.

Do not create GitHub Releases against imported historical source tags. Historical
Agno tags contain original publishers outside the new workflow's gate. See
[MIGRATION.md](../MIGRATION.md) for the history-preservation warning.

## Strands Catalog Provenance Warning

[Strands PR #5852](https://github.com/strands-agents/harness-sdk/pull/5852)
originally reported a mismatch between PyPI's old repository metadata and the
proposed catalog link. The verified 0.1.1 release now advertises the monorepo and
has cryptographically verified publish attestations. The draft description links
to that evidence. The old advisory comment may remain until upstream rechecks it;
the human author's overview, review, and catalog acceptance remain pending.

Published metadata cannot be changed by editing a repository README or PR body.
It must be corrected through a new package release after the publisher cutover.
