# Security Policy

## Reporting A Vulnerability

Do not disclose exploitable vulnerabilities, credentials, customer data, or private
deployment information in a public issue or pull request.

If GitHub private vulnerability reporting is enabled for this repository, use the
**Report a vulnerability** option on its Security tab. This document does not
assert that private reporting is enabled. If that option is unavailable, contact
the repository owner, `@gilarel`, to arrange a private reporting channel before
sending sensitive details. A public request for a private channel must not include
the vulnerability details. No response-time or remediation SLA is promised here.

Include the affected integration and package version or commit, dependency/runtime
versions, impact, and a minimal reproduction with synthetic data. Share secrets
only through an agreed private channel if genuinely needed; normally redact them.
If credentials were exposed, revoke or rotate them promptly rather than waiting
for a repository change to remove the exposure.

## Scope And Known Limits

Reports are welcome for all eight integrations and their packaging/configuration.
This is not a commitment to maintain every historical release. The integrations
have independent versions and upstream framework compatibility requirements;
consult their READMEs when assessing an affected deployment.

The migration validation recorded a clean gitleaks scan of the full imported
48-commit history, including the four Kong commits. A clean scan is not proof of
the absence of secrets or vulnerabilities. The formerly private Kong content was
reviewed for public import, and Agentgateway/Kong MIT licensing was explicitly
approved; neither constitutes a blanket security certification.

The unchanged legacy n8n lockfile produced **24 npm vulnerability reports:
11 moderate, 11 high, and 2 critical** during `npm ci`. n8n lint/build passed,
but the migration did not remediate those findings or establish that the affected
dependencies are safe. `npm audit --omit=dev` reported zero findings; the reported
vulnerabilities are in the development dependency graph. Review exposure and upgrade options
before deployment. Do not confuse a clean secret scan with a clean dependency audit.

Six Python pytest suites passed all 63 tests on Python 3.12 and four Python
packages built during migration validation. These checks do not establish a
security guarantee, complete runtime coverage, or a supported-version matrix.

## Publishing Boundary

No publisher cutover or monorepo releases have occurred. Original repositories
and public publishers remain unchanged. Imported nested workflows are inactive
in the current tree. Root CI does not publish artifacts.

The root monorepo release workflow is manual-dispatch only, gated by
`MONOREPO_PUBLISHING_ENABLED=true` (absent by default), with independent versions,
`<integration>/v<VERSION>` tags, `release-<integration>` job environments, and npm/PyPI
OIDC trusted publishing. Stop old publishers and configure/verify the new bindings
before enabling it. Environment names alone do not establish approval protection.
Historical source tags can contain original publishers outside that gate. Do not
create GitHub Releases against imported source tags, add a repository-wide
`PYPI_API_TOKEN`, or grant registry trust to historical workflow identities.
See [MIGRATION.md](MIGRATION.md) for pending operational gates.
