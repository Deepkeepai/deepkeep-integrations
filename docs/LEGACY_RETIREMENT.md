# Legacy Repository Retirement

The user explicitly approved read-only archival of the five repositories below.
No repositories were deleted, renamed, or made public/private by this operation.
The active integrations monorepo was not archived.

## Approved Batch

Immediately before archival, all five had Admin permission for the acting account,
no open issues or pull requests, and source heads matching their verified notice
merges. After archival, each repository was rechecked: `isArchived=true`, the
same source head, and unchanged visibility.

| Legacy repository | State | Visibility | Preserved main head |
| --- | --- | --- | --- |
| `Deepkeepai/pydantic-ai-deepkeep` | Archived, read-only | Public | `22babd9c7beee14e2cf9462e9f54b58303b41c2b` |
| `Deepkeepai/crewai-tools-deepkeep` | Archived, read-only | Public | `99ab43f196e73905269bf9424bf5609479f6569a` |
| `Deepkeepai/agno-deepkeep` | Archived, read-only | Public | `e0f6b4bb7e0d495f68acb55c5f37263dd785f629` |
| `Deepkeepai/openwebui-deepkeep` | Archived, read-only | Public | `49647b3591826735f92ab4066b0607fce7b915ab` |
| `Deepkeepai/deepkeep-kong-guardrail` | Archived, read-only | Private | `5859c316ab4067498b09be0478a23c8670e3dc33` |

Archival retains the historical code, commits, tags, releases, issues, and PRs
read-only. It is not deletion or a transfer of private data to the public monorepo.
See [GitHub's archival documentation](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories).

## Compatibility Checks

After archival, Open WebUI's historical `v0.1.1` release page still returned HTTP
200, remained a published non-draft release, and both raw filter URLs below were
available with identical content:

- https://github.com/Deepkeepai/openwebui-deepkeep/releases/tag/v0.1.1
- https://raw.githubusercontent.com/Deepkeepai/openwebui-deepkeep/main/deepkeep_openwebui_filter.py
- https://raw.githubusercontent.com/Deepkeepai/openwebui-deepkeep/v0.1.1/deepkeep_openwebui_filter.py

The latest recorded Pydantic AI, CrewAI, and Agno PyPI metadata already points to
their corresponding monorepo directories. No package versions, registry trust,
image tags, or credentials were changed during retirement. The
`MONOREPO_PUBLISHING_ENABLED` gate remains `false`.

## Held Repositories

| Repository | Reason to remain active |
| --- | --- |
| `Deepkeepai/strands-deepkeep` | Hold until the official catalog link update in [PR #5852](https://github.com/strands-agents/harness-sdk/pull/5852) is accepted, avoiding an archived repository as the listed integration source |
| `Deepkeepai/agentgateway-deepkeep-webhook` | Acting account has Write, not Admin; [admin handoff issue #1](https://github.com/Deepkeepai/agentgateway-deepkeep-webhook/issues/1) requests review and archival. Image publishing is already retired and the new publisher verified |

The monorepo and the Dify contribution fork were verified unarchived. LangChain
remains separate and was not changed. No archive operation was submitted outside
the approved five. The separate Agentgateway issue is an admin-review request,
not a completed retirement; the repository remains active until an admin acts.

## Permanent Standalone Boundary

n8n is not a held migration or retirement candidate. At n8n's request and the
user's direction, its canonical source remains
https://github.com/Deepkeepai/n8n-nodes-deepkeep. It is public and active at `main`
`ba711303b21e336a06a8579f2fe321aef9edf4a1`; CI and Release remain active.
It was not archived and its settings were not changed. No npm registry-trust
migration is known and no monorepo npm release occurred. The earlier emailed
monorepo catalog request is superseded; no counterrequest was sent, and catalog
follow-up/live verification remain pending.

The main implementation removes `integrations/n8n` and its root CI/release/script
entries by normal forward deletion. The original eight-import count and source
SHA remain historical facts; older commits retain the code. Preserve history and
namespaced import tags because public PyPI/GHCR source-commit provenance is
immutable: no history rewrite or retagging. The empty `release-n8n` environment
awaits inspection and possible removal only after those code changes merge.
The other five release job environments remain unchanged. The company Cursor
integration is a separate new feature with a different license and is unaffected.

## Remaining Controls

Kong archival freezes historical examples; it does not certify licensed gateway
HTTP/template enforcement. That validation remains pending despite the executable
LuaJIT policy tests in the monorepo.

Archival does not revoke publishing tokens. Agno's old publishing workflow had
already been disabled before the cutover; any old PyPI token requires separate
owner review and revocation only after confirming it is not shared. No publishing
secret values were inspected, copied, deleted, or revoked during retirement.

For migrated integrations, new development, issues, CI validation, and releases
belong in the active monorepo; n8n and LangChain remain separate.
Remaining archives require separate approval. Any future legacy edits
require an explicit decision to unarchive first; do not delete or rewrite
historical references as a shortcut.
