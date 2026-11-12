# DeepKeep Integrations

DeepKeep AI Firewall integrations for agent frameworks, gateways, and automation
platforms. Each integration keeps its own dependencies, tests, and release version.

| Integration | Installation or usage |
| --- | --- |
| [Agentgateway](integrations/agentgateway/) | HTTP webhook adapter and container |
| [Open WebUI](integrations/openwebui/) | Importable Python filter function |
| [Strands](integrations/strands/) | `pip install strands-deepkeep` |
| [Agno](integrations/agno/) | `pip install agno-deepkeep` |
| [CrewAI](integrations/crewai/) | `pip install crewai-tools-deepkeep` |
| [Kong](integrations/kong/) | AI Custom Guardrail configuration examples |
| [Pydantic AI](integrations/pydantic-ai/) | `pip install pydantic-ai-deepkeep` |
| [Cursor](integrations/cursor/) | Cursor plugin for DeepKeep guardrails |

See each integration's README for supported versions, configuration, and examples.
Do not put API keys or customer data in issues, examples, or pull requests.
n8n is maintained separately in [n8n-nodes-deepkeep](https://github.com/Deepkeepai/n8n-nodes-deepkeep)
and is not built or published from this repository.

## Development

Work inside the integration directory and use a separate environment for each
Python integration. There is no shared root package or combined release version.
See [CONTRIBUTING.md](CONTRIBUTING.md) for validation commands.

## Migration

The original eight integrations were imported with history. n8n has since been
excluded at its maintainers' request and remains standalone; its imported history
and tags are retained, not rewritten. The remaining integrations keep their
package names, Python imports, and existing container endpoint. Original
repositories remain available for compatibility. The four Python metadata
releases and Agentgateway image 0.1.0 are now [published and verified](docs/RELEASES.md).
Agno's old publisher is disabled; Agentgateway's old CI still tests/builds but no
longer pushes images.
Five retired repositories are now read-only archives with historical code and
release/raw URLs preserved; see [retirement status](docs/LEGACY_RETIREMENT.md).
See [MIGRATION.md](MIGRATION.md) for imported commits and publishing cutover status,
and [the reference tracker](docs/REFERENCE_AUDIT.md) for upstream documentation.

## License

MIT unless otherwise stated in an integration's license. The Cursor integration is Apache-2.0.
