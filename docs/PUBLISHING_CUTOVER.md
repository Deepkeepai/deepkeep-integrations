# Publishing Cutover

Initial audit: 2026-11-05. All four Python metadata releases were published and
verified on 2026-11-08; see [RELEASES.md](RELEASES.md). No container image or npm
package has been published here. Only Agno's old `publish.yml` was disabled,
with explicit authorization; its test workflow remains active.

## Verified State

- `MONOREPO_PUBLISHING_ENABLED` is explicitly `false`.
- Imported source revisions and ancestry are recorded in `MIGRATION.md`; the
  monorepo packages include subsequent metadata, documentation, and version edits.
- Six GitHub environments exist, each requiring reviewer `gilarel` and allowing
  deployments only from branch `main`: `release-n8n`, `release-agentgateway`,
  `release-strands`, `release-agno`, `release-crewai`, `release-pydantic-ai`.
- Self-review is allowed, so the author can explicitly approve a manually
  dispatched release. This is an approval gate, not two-person separation of duty.
  Repository administrators can change protection settings; do not treat names
  or reviewer configuration as immutable security boundaries.
- No repository Actions secrets were copied. npm/PyPI publication uses OIDC;
  Agentgateway uses GitHub's automatically supplied `GITHUB_TOKEN`.
- All four PyPI runs succeeded after environment approval. The last three reviews
  were submitted through the CLI at the owner's explicit request, not browser
  clicks. Their artifacts and installed-wheel tests verified. Successful CI by
  itself is not proof of registry publishing authorization.

## Registry Bindings To Configure

These are required settings. All four PyPI paths have been demonstrated by
successful attested publications; npm and GHCR permissions remain unverified.
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
| PyPI | `agno-deepkeep` | `release-agno` | `0.1.2`, verified publication |
| PyPI | `crewai-tools-deepkeep` | `release-crewai` | `0.1.3`, verified publication |
| PyPI | `pydantic-ai-deepkeep` | `release-pydantic-ai` | `0.1.1`, verified publication |

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

Settings: https://github.com/orgs/Deepkeepai/packages/container/agentgateway-deepkeep-webhook/settings
Under **Manage Actions access**, add `Deepkeepai/deepkeep-integrations` with
**Write** permission. Do not change visibility, inheritance, or the linked source
repository as a side effect. This ACL has no documented public REST write endpoint;
the package administrator must use the authenticated settings page.

The container workflow now performs read-only registry preflight: it requires
the selected version to be absent and captures the existing `latest` digest.
After pushing, it requires both tags to match the build digest. These checks use
the job token without printing credentials and fail closed on unexpected registry
responses. They do not grant the repository access or prove write permission
before a successful push. If postflight fails, inspect the registry before any
retry; do not overwrite a version that may already have been published.

The current CLI token lacks `read:packages`; the package API returned HTTP 403.
Package association, inherited permissions, visibility, and current image digests
therefore remain unverified. Granting a token scope requires the account owner's
approval; no authentication scopes were changed during this audit.

## Coordinate Existing Publishers

| Integration | Existing publication path | Cutover requirement |
| --- | --- | --- |
| n8n | Active `release.yml`, triggered by `v*.*.*` tag pushes, npm OIDC/provenance | Coordinate and stop the old release publisher before the new publisher is enabled |
| Agentgateway | Active `ci.yml`, pushes images on source `main` updates | Stop old image pushes while retaining tests if desired; otherwise the old repository can overwrite `latest` |
| Agno | Old `publish.yml` used `PYPI_API_TOKEN`; now `disabled_manually` | Disabled before the approved monorepo 0.1.2 publication; tests remain active. Token removal/revocation is separate owner cleanup |
| Strands | No repository-defined old publisher found | Monorepo 0.1.1 verified; keep old manual upload paths idle |
| CrewAI | No repository-defined old publisher found | Monorepo 0.1.3 verified; keep old manual upload paths idle |
| Pydantic AI | No repository-defined old publisher found | Monorepo 0.1.1 verified; keep old manual upload paths idle |

Absence of a checked-in workflow does not prove there is no publisher. Original
repositories were authoritative before the approved cutovers. The four Python
projects now have verified monorepo publication paths. Do not
disable unrelated workflows or archive repositories as a side effect.

## Prepare Fresh Versions

The imported npm/PyPI package versions matched already published versions.
The [four Python metadata patches](PYTHON_RELEASE_CANDIDATES.md) have now been
published and cannot be reused. For any future release, prepare another reviewed,
unused version bump and rerun tests/build/artifact checks before creating its tag.
Do not use republishing as a permission test. n8n remains paused separately.

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
has cryptographically verified publish attestations. The PR description links
to that evidence. The old advisory comment may remain until upstream rechecks it;
the human author has now supplied the overview and confirmed review. The PR is
ready for maintainer review; acceptance remains pending.

Published metadata cannot be changed by editing a repository README or PR body.
It must be corrected through a new package release after the publisher cutover.
