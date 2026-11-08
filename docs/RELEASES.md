# Verified Monorepo Releases

Only releases listed here have been published and checked. Prepared versions,
Git tags, and successful CI alone are not evidence of registry publication.

## strands-deepkeep 0.1.1

- PyPI: https://pypi.org/project/strands-deepkeep/0.1.1/
- Release workflow: https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42225772581
- Tag: `strands/v0.1.1`, resolving to `4ca53d058c7ec3f34fa22b70dce6ec923b636feb`.
- Dispatch: `workflow_dispatch` on `main`; environment `release-strands`, approved by `gilarel`.
- Uploaded on 2026-11-08 at 16:14 UTC. No GitHub Release was created.
- The global publishing gate was restored to `false`; the other integration publishers were not dispatched.

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

The verified certificates identify GitHub Actions, `release.yml`, environment
`release-strands`, run `42225772581` attempt 1, and commit
`4ca53d058c7ec3f34fa22b70dce6ec923b636feb`. The signed ref is
`refs/heads/main`, not the tag. The tag resolves to that same commit, and the
workflow passes its resolved commit to the publisher checkout. These are PyPI
publish attestations, not separate SLSA build-provenance statements or proof of
reproducible builds. The annotated tag itself is unsigned.

### Installation Verification

Installed `strands-deepkeep==0.1.1` from PyPI in a fresh Python 3.12.16 environment,
confirmed the version and import location under that environment's `site-packages`,
and ran the existing suite outside the source tree: **10 passed, no skips**.
The tests use mocked HTTP/clients; live DeepKeep services were not exercised.
The sdist was verified but not independently rebuilt and tested.

Published Repository and Documentation URLs now point to `integrations/strands`
in this monorepo. This addresses the old-repository mismatch reported on the
Strands catalog draft; upstream review, human overview, merge, and live catalog
verification remain separate pending actions.
