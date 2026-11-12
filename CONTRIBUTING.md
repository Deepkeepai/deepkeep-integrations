# Contributing

Work in the relevant `integrations/<name>` directory. Each integration has its own
dependencies and version; there is no root Python package or combined release.
Read its README before changing supported APIs, configuration, or examples.

## Local Validation

Use a separate virtual environment for each Python integration. Python 3.12 is
the migration validation baseline, not a claim that every supported version has
been tested. From the integration directory, create and activate an environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

For `agno`, `crewai`, `pydantic-ai`, and `strands`:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m pip install build
python -m build
```

For `agentgateway` and `openwebui`, install their development requirements instead:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

Do not install all integrations into one environment to resolve incompatible
framework dependencies. Open WebUI is an importable filter, not one of the four
distributable Python packages. Kong is not a Python distribution, but its
`requirements-dev.txt` and pytest suite execute the embedded LuaJIT policies.
Run those checks in its directory; deployed gateway validation is separate.

n8n is permanently outside this monorepo. Contribute and validate in its active
standalone repository: https://github.com/Deepkeepai/n8n-nodes-deepkeep.
`integrations/n8n` is removed from the current-tree scope; older commits retain it.

The migration baseline recorded six Python suites passing all 63 tests, all four
Python packages building, and the originally imported n8n snapshot's lint/build
passing. These are historical local validation results, not proof of production
compatibility. Root CI runs path-selected checks
and provides an aggregate `CI status` check. Imported `.github/workflows`
directories underneath integrations are retained provenance, not active workflows
in the current tree. Historical tag workflows require separate precautions in
[MIGRATION.md](MIGRATION.md).

During the 2026-11-05 migration validation, `npm ci` reported **24 vulnerabilities:
11 moderate, 11 high, and 2 critical** in the imported n8n snapshot's unchanged
lockfile. This is not a current-tree dependency finding or a fresh audit of the
standalone repository. Passing lint/build did not establish dependency safety.

The [initial GitHub CI run](https://github.com/Deepkeepai/deepkeep-integrations/actions/runs/42054023512)
also passed all integration, artifact, workflow, and container checks.

## Changes And Review

- Keep changes scoped to the integration and include relevant tests and docs.
- State the commands run, results, and any validation not performed in the PR.
- Preserve package names, Python imports, and the existing container endpoint
  unless an explicitly reviewed compatibility change requires otherwise.
- Never include API keys, customer data, real prompts containing sensitive data,
  or private deployment details. Use placeholders and synthetic test fixtures.
- Retain license notices and provenance. See [MIGRATION.md](MIGRATION.md) before
  changing history, upstream references, or publishing configuration.

`@gilarel` is the code owner recorded in `.github/CODEOWNERS`. That file identifies
an owner; it does not itself enforce reviews or branch protection.

## Releases And External Changes

The four Python metadata releases are [published and verified](docs/RELEASES.md).
Agentgateway image 0.1.0 is also verified. Agno's old publisher is disabled;
Agentgateway's old CI builds/tests without pushing. Five other legacy repositories
are now archived read-only; use monorepo CI for active validation. See
[retirement status](docs/LEGACY_RETIREMENT.md) for the exact archived and held set.
Do not publish from this repository,
disable old publishers, submit upstream migration PRs, or archive source repos as
part of a routine contribution. See the cutover gates in [MIGRATION.md](MIGRATION.md)
and the pending actions in [docs/REFERENCE_AUDIT.md](docs/REFERENCE_AUDIT.md).

The root release workflow is manual-dispatch only and disabled unless repository
variable `MONOREPO_PUBLISHING_ENABLED` is exactly `true` (absent by default).
Integration versions are independent, tags use `<integration>/v<VERSION>`, and jobs
use `release-<integration>` environments for five publishable distributions: four
PyPI packages and the Agentgateway GHCR image. PyPI publishing uses OIDC trusted
publishing. n8n/npm releases are excluded; leave the standalone CI and Release
workflows active. Old publishers for in-scope cutovers must be stopped and new
trust/environment bindings configured and verified before enabling it. Workflow deployment does not
configure registry trust or environment protection rules. Never create GitHub
Releases against imported historical source tags; they can contain old publishers.
