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
distributable Python packages. Kong provides configuration examples, not a Python
package or pytest suite; check examples against the intended Kong version.

For n8n, from `integrations/n8n`, use the Node.js version supported by its tooling:

```powershell
npm ci
npm run lint
npm run build
```

The migration baseline recorded six Python suites passing all 63 tests, all four
Python packages building, and n8n lint/build passing. These are local validation
results, not proof of production compatibility. Root CI runs path-selected checks
and provides an aggregate `CI status` check. Imported `.github/workflows`
directories underneath integrations are retained provenance, not active workflows
in the current tree. Historical tag workflows require separate precautions in
[MIGRATION.md](MIGRATION.md).

`npm ci` reported **24 vulnerabilities: 11 moderate, 11 high, and 2 critical**.
The legacy n8n lockfile was left unchanged. Passing lint/build and moving source
do not make these dependencies safe. Investigate dependency upgrades separately;
do not apply a blanket force-fix or silently rewrite the lockfile in a docs change.

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
Only Agno's old publishing workflow was disabled; original tests remain active.
Do not publish from this repository,
disable old publishers, submit upstream migration PRs, or archive source repos as
part of a routine contribution. See the cutover gates in [MIGRATION.md](MIGRATION.md)
and the pending actions in [docs/REFERENCE_AUDIT.md](docs/REFERENCE_AUDIT.md).

The root release workflow is manual-dispatch only and disabled unless repository
variable `MONOREPO_PUBLISHING_ENABLED` is exactly `true` (absent by default).
Integration versions are independent, tags use `<integration>/v<VERSION>`, and jobs
use `release-<integration>` environments. npm/PyPI publishing uses
OIDC trusted publishing. Old publishers must be stopped and new trust/environment
bindings configured and verified before enabling it. Workflow deployment does not
configure registry trust or environment protection rules. Never create GitHub
Releases against imported historical source tags; they can contain old publishers.
