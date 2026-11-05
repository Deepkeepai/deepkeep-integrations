# Python Metadata Release Candidates

These patch versions were approved and merged to `main` in
[PR #1](https://github.com/Deepkeepai/deepkeep-integrations/pull/1), but are not
published. No release tags or GitHub Releases have been created. n8n is excluded.

| Integration | Distribution | Published version | Proposed version |
| --- | --- | --- | --- |
| Strands | `strands-deepkeep` | `0.1.0` | `0.1.1` |
| Agno | `agno-deepkeep` | `0.1.1` | `0.1.2` |
| CrewAI | `crewai-tools-deepkeep` | `0.1.2` | `0.1.3` |
| Pydantic AI | `pydantic-ai-deepkeep` | `0.1.0` | `0.1.1` |

The proposed versions were unused in public PyPI metadata when checked on
2026-11-05. Recheck immediately before publication; this does not reserve them.

## Validation

Each candidate was installed and tested in a separate Python 3.12.16 environment.
All 38 integration tests and six root release-validator tests passed. Each
package produced a wheel and source distribution; all eight artifacts passed
`twine check`. Wheel metadata confirms the proposed versions and new repository
and documentation URLs. Tag-string validation passed without creating any tags.
No model API calls, registry uploads, or publisher cutover were performed.

## Changes Since The Standalone Distributions

- Repository and documentation metadata points to the exact monorepo directory.
- Package names, import paths, and runtime behavior are preserved.
- The build backend minimum supports the SPDX license metadata; CrewAI explicitly
  declares MIT, matching its retained license file.
- The guides distinguish accepted listings from declined or pending proposals.
- OpenAI-backed examples document their required provider dependencies and keys;
  the CrewAI guide includes the previously missing Agent construction/import.

This release preparation changes only package versions and documentation. It
does not merge the four integration APIs or impose a shared runtime dependency.

## Before Publishing

Follow [PUBLISHING_CUTOVER.md](PUBLISHING_CUTOVER.md). Each selected project needs
verified ownership, an exact PyPI trusted publisher for `release.yml` and its
`release-<integration>` environment, coordination of any old upload process, and
explicit release approval. Keep the global publishing gate false until those
requirements are met. CI builds and uploads are not registry publications.

The preparation merge is complete. Only after registry setup, fresh validation,
and explicit release approval, create a new immutable monorepo tag matching the
selected package version. Do not reuse imported historical tags or create releases
against their original source commits.

Publishing new Strands metadata will allow its catalog reviewers to recheck the
old-repository mismatch. Until then, the source-history evidence is in the draft
upstream PR; it is not proof of registry-side trust or a completed catalog update.
