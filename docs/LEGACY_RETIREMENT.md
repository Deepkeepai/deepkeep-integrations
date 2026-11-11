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
| `Deepkeepai/agentgateway-deepkeep-webhook` | Acting account has Write, not Admin; a repository admin or organization owner must approve and perform archival. Image publishing is already retired and the new publisher verified |
| `Deepkeepai/n8n-nodes-deepkeep` | Source/publisher migration remains paused; existing publishing was not changed. Its emailed catalog request awaits response/live verification |

The monorepo and the Dify contribution fork were verified unarchived. LangChain
remains separate and was not changed. No repository outside the approved five
was submitted for archival.

## Remaining Controls

Kong archival freezes historical examples; it does not certify licensed gateway
HTTP/template enforcement. That validation remains pending despite the executable
LuaJIT policy tests in the monorepo.

Archival does not revoke publishing tokens. Agno's old publishing workflow had
already been disabled before the cutover; any old PyPI token requires separate
owner review and revocation only after confirming it is not shared. No publishing
secret values were inspected, copied, deleted, or revoked during retirement.

New development, issues, CI validation, and releases belong in the active
monorepo. Remaining archives require separate approval. Any future legacy edits
require an explicit decision to unarchive first; do not delete or rewrite
historical references as a shortcut.
