# DeepKeep Integrations

DeepKeep AI Firewall integrations for agent frameworks, gateways, and automation
platforms. Each integration keeps its own dependencies, tests, and release version.

| Integration | Installation or usage |
| --- | --- |
| [n8n](integrations/n8n/) | `n8n-nodes-deepkeep` community node |
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

## Development

Work inside the integration directory and use a separate environment for each
Python integration. There is no shared root package or combined release version.
See [CONTRIBUTING.md](CONTRIBUTING.md) for validation commands.

## Migration

This repository consolidates the eight standalone integrations without changing
their package names, Python imports, or existing container endpoint. Original
repositories remain available for compatibility. The four Python metadata
releases and Agentgateway image 0.1.0 are now [published and verified](docs/RELEASES.md).
Agno's old publisher is disabled; Agentgateway's old CI still tests/builds but no
longer pushes images. See
[MIGRATION.md](MIGRATION.md) for imported commits and publishing cutover status,
and [the reference tracker](docs/REFERENCE_AUDIT.md) for upstream documentation.

## License

MIT unless otherwise stated in an integration's license. The Cursor integration is Apache-2.0.
