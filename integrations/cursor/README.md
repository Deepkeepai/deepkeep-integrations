# DeepKeep guardrails for Cursor

The Cursor plugin checks prompts, shell commands, file reads, and MCP tool calls
against a configured DeepKeep policy endpoint. It does not check file writes.
Prompt attachments are sent as paths, not file contents.

## Build and test

Install Node.js 20 or later for development, then run:

```bash
npm ci
npm test
npm run typecheck
npm run build:plugin
```

The built plugin is in `cursor-plugin/`. Its launchers find a compatible
JavaScript runtime on the machine or in Cursor.

## Install from the repository

1. In Cursor, open **Customize** and choose **Add from Repo**.
2. Enter
   `https://github.com/Deepkeepai/deepkeep-integrations/tree/main/integrations/cursor`.
3. Select the DeepKeep plugin and install it.
4. In Cursor chat, run `/deepkeep-connect` and follow the configuration
   instructions. Enter your API key privately, outside chat and agent tools.
5. Fully quit and reopen Cursor.

## Install from a team marketplace

Team marketplaces require a Cursor Teams or Enterprise plan. A Cursor team
administrator can make the plugin available to the team:

1. Open the [Cursor Plugins & MCPs dashboard](https://cursor.com/dashboard/plugins).
2. Under **Team Marketplaces**, choose **Add Marketplace**, then
   **Import from Repo**.
3. Enter `https://github.com/Deepkeepai/deepkeep-integrations` and follow the
   prompts to add the marketplace.
4. Verify the marketplace and its DeepKeep plugin appear in the dashboard.
   Set marketplace access and the plugin installation mode for your team.

Team members can then open **Customize** in Cursor and install the DeepKeep
plugin if it is not installed automatically. Follow the
[plugin configuration guide](cursor-plugin/README.md#configuration), or run
`/deepkeep-connect` in Cursor chat. Enter your API key privately, outside chat
and agent tools, then fully quit and reopen Cursor.

## Local installation

Run `npm run install:plugin`, then fully quit and reopen Cursor. The command
replaces any existing local DeepKeep plugin. Cursor Enterprise administrators
may need to allow local plugin imports.

The plugin registers its own hooks and does not edit `~/.cursor/hooks.json`.
Remove any DeepKeep entries left there by the old installer to avoid running
duplicate hooks.

## Configuration

The plugin is free, but requires a paid DeepKeep API token to function.

Create `~/.deepkeep/config.json` with your DeepKeep endpoint and API key:

```json
{
  "firewallUrl": "https://api.<tenant>.deepkeep.ai/api/v2/developer-agent/validate",
  "apiKey": "<your-api-key>",
  "failMode": "block",
  "timeoutMs": 2500,
  "cacheTtlMs": 300000
}
```

An optional `bearerToken` can also be supplied. Keep all credentials private.
Create the directory with permissions `0700` and the file with permissions
`0600`. Enter the key privately, outside Cursor chat and agent tools.

The file takes precedence over environment variables for `firewallUrl`, `apiKey`,
`bearerToken`, and `failMode`. An HTTPS endpoint is required. Each hook reads the
configuration when it runs, so changing the endpoint or key does not require a
rebuild.

The environment variables `DEEPKEEP_TIMEOUT_MS` and `DEEPKEEP_CACHE_TTL_MS`
take precedence over the corresponding file values. `cacheTtlMs` defaults to
300,000 ms, but the current plugin does not use it or cache policy decisions.

`failMode` defaults to `block`. With `allow`, an action can proceed unchecked
when validation fails. Hook inputs over 5 MiB follow this setting. The API
truncates serialized payloads over 32,768 characters before inspection, so a
decision may not cover the full action. Plugin startup failures are
configured to block independently of `failMode`.

The policy request timeout defaults to 2,500 ms and is capped at 5,000 ms to
leave time before Cursor's hook deadline. Startup delays can still cause Cursor
to block a hook before the configured failure mode is applied.

The plugin and its configuration are user-writable. They are not a
tamper-resistant enforcement boundary.

## Data use

Prompt text, shell commands, file contents, and MCP tool inputs are sent to the
customer's configured DeepKeep endpoint for validation and auditing. The
customer handles the data. Retention is 90 days and configurable. Prompt
attachments are sent as paths, not contents. DeepKeep does not use plugin data
to train AI or machine learning models.

Data is hosted on the customer's premises or in DeepKeep's SaaS environment.
DeepKeep staff have no access on premises and have authorized access in SaaS.
DeepKeep can delete data upon customer request.

## Check the connection

From the repository, run:

```bash
node cursor-plugin/bin/cli.js doctor
```

This sends a test prompt to the configured policy endpoint. Hook decisions and
errors are logged in `~/.deepkeep/logs/hook.log`. Do not share API keys or
customer data in support requests.

## Uninstall the local plugin

Run `bash scripts/uninstall-from-cursor.sh`, then fully quit and reopen Cursor.
The script leaves `~/.deepkeep/` intact and warns about old user-level hooks.

## Guides

- [Plugin documentation](cursor-plugin/README.md)
- [Website privacy policy](https://www.deepkeep.ai/privacy-policy)
- [Platform terms](https://www.deepkeep.ai/platform-terms-and-conditions)

## License

Apache License 2.0. See [LICENSE](LICENSE).
