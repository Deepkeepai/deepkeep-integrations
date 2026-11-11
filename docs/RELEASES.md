# Verified Monorepo Releases

Only releases listed here have been published and checked. Prepared versions,
Git tags, and successful CI alone are not evidence of registry publication.

## strands-deepkeep 0.1.1

- PyPI: https://pypi.org/project/strands-deepkeep/0.1.1/
- Release workflow: https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42225772581
- Tag: `strands/v0.1.1`, resolving to `4ca53d058c7ec3f34fa22b70dce6ec923b636feb`.
- Dispatch: `workflow_dispatch` on `main`; environment `release-strands`, approved by `gilarel`.
- Uploaded on 2026-11-08 at 16:14 UTC. No GitHub Release was created.
- The global publishing gate was restored to `false`; only Strands was selected in this run.

### Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `strands_deepkeep-0.1.1-py3-none-any.whl` | `71ea7166939f3f72d6dac533cf83866e44b9b4ff519a95185a759c939edff8df` |
| `strands_deepkeep-0.1.1.tar.gz` | `7a7498545477e3d0619d4a94b58d8a2ec140cf099e8a22012e8fdfd4db553711` |

Both artifacts were downloaded and their SHA-256 values independently recomputed.
Both public PyPI publish attestations were cryptographically verified using
`pypi-attestations==0.0.31`, with the expected monorepo repository identity:

```text
python -I -m pypi_attestations verify pypi --repository https://github.com/Deepkeepai/deepkeep-integrations pypi:strands_deepkeep-0.1.1-py3-none-any.whl
python -I -m pypi_attestations verify pypi --repository https://github.com/Deepkeepai/deepkeep-integrations pypi:strands_deepkeep-0.1.1.tar.gz
```

The verified certificates identify GitHub Actions, `release.yml`,
run `42225772581` attempt 1, and commit
`4ca53d058c7ec3f34fa22b70dce6ec923b636feb`. The signed ref is
`refs/heads/main`, not the tag. The tag resolves to that same commit, and the
workflow passes its resolved commit to the publisher checkout. These are PyPI
publish attestations, not separate SLSA build-provenance statements or proof of
reproducible builds. The annotated tag itself is unsigned. The environment name
comes from public Integrity API publisher metadata and the approved GitHub
deployment, not a signed certificate environment claim.

### Installation Verification

Installed `strands-deepkeep==0.1.1` from PyPI in a fresh Python 3.12.16 environment,
confirmed the version and import location under that environment's `site-packages`,
and ran the existing suite outside the source tree: **10 passed, no skips**.
The tests use mocked HTTP/clients; live DeepKeep services were not exercised.
The sdist was verified but not independently rebuilt and tested.

Published Repository and Documentation URLs now point to `integrations/strands`
in this monorepo. This addresses the old-repository mismatch reported on the
Strands catalog PR. The human author has now supplied the overview, confirmed
review, and authorized marking it ready. Maintainer acceptance, merge, and live
catalog verification remain separate pending actions.

## Remaining Python Metadata Releases

These three releases were explicitly authorized after Strands verification.
The `gilarel` owner separately authorized submitting the deployment approvals
through the CLI, which was recorded in each approval comment. The global gate
was restored to `false` once all validation jobs passed.

| Distribution | Version | Tag | Successful workflow |
| --- | --- | --- | --- |
| `agno-deepkeep` | `0.1.2` | `agno/v0.1.2` | [42502197736](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42502197736) |
| `crewai-tools-deepkeep` | `0.1.3` | `crewai/v0.1.3` | [42502201501](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42502201501) |
| `pydantic-ai-deepkeep` | `0.1.1` | `pydantic-ai/v0.1.1` | [42502204226](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42502204226) |

All three annotated tags resolve to
`0fc63daf720aff9525ac64764ccc8794907b0988`. No GitHub Releases were created.
Before dispatch, Agno's standalone `publish.yml` was explicitly disabled to avoid
competing publishers; its `Test` workflow was left active at cutover. The legacy
repo was later archived in the [approved retirement batch](LEGACY_RETIREMENT.md).
No other old workflow
was disabled. n8n, LangChain, and the Agentgateway publisher were not changed.

### Artifact Verification

All six artifacts were downloaded independently and their SHA-256 values matched
the version-specific PyPI metadata and verified publish-attestation subjects.
Official `pypi-attestations==0.0.31` verified each artifact sequentially.

| Artifact | Uploaded UTC on 2026-11-08 | SHA-256 |
| --- | --- | --- |
| `agno_deepkeep-0.1.2-py3-none-any.whl` | `17:06:07.935707Z` | `9477df1a06e6bcdc7d25c3506829c0213a0d06a8f8cab78389e5893c916bc400` |
| `agno_deepkeep-0.1.2.tar.gz` | `17:06:09.303350Z` | `4bea160de9e0556101bf5c22962efe6add0d3e808a4a4a74c3abede4800d36c6` |
| `crewai_tools_deepkeep-0.1.3-py3-none-any.whl` | `17:06:32.230279Z` | `c2b5f1737a2ab34466bac144471468e7f706608a65d153798236e41a22a13b1c` |
| `crewai_tools_deepkeep-0.1.3.tar.gz` | `17:06:33.445913Z` | `37f89be4f18f1458fadb26c7745db921e157a1fe3997bb7a959192d7363231e8` |
| `pydantic_ai_deepkeep-0.1.1-py3-none-any.whl` | `17:06:10.926713Z` | `bdccd13845b65e9777ee1e8407042f2798b7a8374b10b9509eec623c84c424b7` |
| `pydantic_ai_deepkeep-0.1.1.tar.gz` | `17:06:12.368473Z` | `ad42a22c84e0c325a50e2b5120c1ca1a4cad6de5892fb1f286a930d898d9f6e9` |

Verified certificate identities consistently name this repository,
`.github/workflows/release.yml@refs/heads/main`, the corresponding run at attempt 1,
and commit `0fc63daf720aff9525ac64764ccc8794907b0988`. The trigger is
`workflow_dispatch`. Integrity API publisher metadata reports `release-agno`,
`release-crewai`, and `release-pydantic-ai`; these environment names are not signed
certificate claims. The same publish-attestation and unsigned-tag limits described
for Strands apply here. No source distribution was independently rebuilt.

### Installed-Wheel Tests

Each wheel was installed from PyPI with all declared dependencies in a fresh
Python 3.12.16 environment. Import versions and paths were checked under each
environment's `site-packages`, not local source. `pip check` passed for all three.
Existing tests ran from outside the repository with isolated Python/importlib
mode and repository pytest configuration disabled.

| Package | Tests passed | Skipped |
| --- | --- | --- |
| Agno | 13 | 0 |
| CrewAI | 6 | 0 |
| Pydantic AI | 9 | 0 |

Together with Strands, all four published wheels passed **38 tests**. Live model
and DeepKeep calls were not exercised. Registry publication does not by itself
complete upstream documentation reviews, Open WebUI listing edits,
Kong runtime validation, or original-repository archival.

## Agentgateway 0.1.0

Published image: `ghcr.io/deepkeepai/agentgateway-deepkeep-webhook:0.1.0`.
At publication and the separate verification run, `latest` resolved to the same
OCI image-index digest:

```text
sha256:a21ac055ca8603c63ea9e93979f4532b302c7b9a4cf1e69607549a877ddd909a
```

Previous `latest` digest, recorded before the push:

```text
sha256:2df68cff99f320143c4bc066b7263d39e56be251793553aecb2b345f534cbb39
```

The previous digest is a rollback reference, not a guarantee of future registry
retention. No rollback, image deletion, package-visibility change, inheritance
change, or explicit repository relinking was performed.

### Publication Evidence

- Release: https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42584070541
- Tag: `agentgateway/v0.1.0`, resolving to `542b763d939c166dd21b2624b816c333a5f7ba97`.
- Published on 2026-11-09; build/push completed at 08:11:51 UTC and postflight at 08:11:52 UTC.
- Environment: `release-agentgateway`, approved through the CLI at the explicit request of the `gilarel` owner.
- The application source is byte-for-byte identical to the originally imported adapter; all 13 application tests passed in the release job.
- Preflight required an unused `0.1.0` tag and captured the existing latest digest.
- Buildx pushed both tags with the digest above; authenticated postflight required both registry HEAD digests to match that build output.
- The global publishing gate was restored to `false` after validation. Python/n8n publishers were not selected in this run.

### Independent Pull And Runtime Check

[Verification run 42585703883](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42585703883)
used a separate job with `contents: read` and `packages: read`, not publishing
permissions. It rechecked both registry tags, pulled the immutable digest, and
started the image without published ports, host mounts, network access, real API
keys, or elevated capabilities. CPU, memory, and process limits were applied.
`GET /healthz` inside the container returned HTTP 200 and exactly
`{"status": "ok"}`. The container was removed afterward. This verifies image
pull/startup/health, not live DeepKeep moderation or an agentgateway deployment.

The descriptor is `application/vnd.oci.image.index.v1+json`. Build logs show a
provenance-attestation export, but no cryptographic container-attestation or
SLSA verification was performed. Do not conflate this image verification with the
cryptographic PyPI publish-attestation checks recorded above.

### Legacy Repository

The old repository now points to the monorepo and retains its source and URLs.
Commit `c3bbe8d88fbd944f1498592c7725ed224c1dc16b` removes `packages: write` and the
registry login from legacy CI and sets Docker `push: false`. Its test and build
jobs remain active; [legacy CI run 42583755756](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook/actions/runs/42583755756)
passed both jobs, including all 13 tests and compilation. No old image push was
in progress at cutover. The repository was not archived or deleted.
