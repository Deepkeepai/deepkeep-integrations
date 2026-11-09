# DeepKeep guardrails for Cursor

Checks prompts, shell commands, file reads, and MCP tool calls against your
organization's DeepKeep policies before they reach the model or run on your
machine. The configured failure mode controls what happens if validation fails.

## What it does

The plugin registers four Cursor hooks. Each one sends the pending action to
your DeepKeep policy endpoint and either allows it or blocks it with an
explanation.

| Cursor hook | Checks |
| --- | --- |
| `beforeSubmitPrompt` | prompt text and attachment paths |
| `beforeShellExecution` | the command and working directory |
| `beforeReadFile` | the file path and contents |
| `beforeMCPExecution` | the MCP server, tool name, and tool input |

All four are configured `failClosed`, so if the plugin cannot run, the action
is blocked. If the policy service cannot be reached, `failMode` controls the
result and defaults to `block`. Set it to `allow` to let actions proceed unchecked.
The API truncates serialized payloads over 32,768 characters before inspection,
so a decision may not cover the full action.
Hook inputs over 5 MiB also follow `failMode` before payload parsing.

## Requirements

The plugin is free, but requires a paid DeepKeep API token to function.

No manual runtime install. The plugin ships a self-contained JavaScript bundle
and locates a runtime automatically, preferring `node` on your `PATH` and
falling back to the runtime shipped with Cursor.

Supported on macOS, Linux, and Windows.

## Configuration

Set the policy endpoint and API key in `~/.deepkeep/config.json`:

```json
{
    "firewallUrl": "https://api.<tenant>.deepkeep.ai/api/v2/developer-agent/validate",
    "apiKey": "<your api key>",
    "failMode": "block"
}
```

Create the directory with mode `0700` and the file with mode `0600`. Enter
the API key privately, outside Cursor chat and agent tools.

After configuring, fully quit Cursor (Cmd+Q / Alt+F4) and reopen it.

## Verifying it is working

```bash
tail -f ~/.deepkeep/logs/hook.log
```

Send a prompt or run a shell command in Cursor; you should see a decision
logged for the corresponding hook.

## Privacy

Prompt text, shell commands, file contents, and MCP tool inputs are sent to the
DeepKeep endpoint you configure for validation. Prompt attachments are sent as
paths, not contents. Hook inputs are limited to 5 MiB. Your API key is stored
locally in `~/.deepkeep/config.json` and is never written to logs.

The customer handles this data for auditing. Retention is 90 days and
configurable. DeepKeep does not use plugin data to train AI or machine learning
models.

Data is hosted on the customer's premises or in DeepKeep's SaaS environment.
DeepKeep staff have no access on premises and have authorized access in SaaS.
DeepKeep can delete data upon customer request.

See DeepKeep's [website privacy policy](https://www.deepkeep.ai/privacy-policy) and
[platform terms](https://www.deepkeep.ai/platform-terms-and-conditions).

## Support

- Documentation: https://deepkeep.ai
- Issues: https://github.com/Deepkeepai/deepkeep-integrations/issues
