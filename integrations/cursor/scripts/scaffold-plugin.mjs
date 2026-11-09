#!/usr/bin/env node
// Recreate the static Cursor plugin scaffold on every plugin build.
// This keeps `npm run build:plugin` idempotent even if `cursor-plugin/`
// was deleted, extracted partially, or contains stale files from an
// earlier scaffold. We nuke the managed subpaths first, then re-write.
//
// `bin/` is NOT managed here. It holds hand-written launchers
// (`deepkeep-hook`, `deepkeep-hook.cmd`, `run.ps1`) plus the CLI bundle
// that `bundle-into-plugin.mjs` copies in afterwards.

import { chmodSync, copyFileSync, mkdirSync, rmSync, writeFileSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, "..")
const pluginRoot = join(repoRoot, "cursor-plugin")

const MANAGED_SUBPATHS = [".cursor-plugin", "hooks", "commands", "assets", "README.md"]
for (const sub of MANAGED_SUBPATHS) {
    rmSync(join(pluginRoot, sub), { recursive: true, force: true })
}

function write(relPath, contents, mode) {
    const path = join(pluginRoot, relPath)
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, contents)
    if (mode != null) chmodSync(path, mode)
}

for (const file of ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES"]) {
    copyFileSync(join(repoRoot, file), join(pluginRoot, file))
}

write(".cursor-plugin/plugin.json", `{
    "name": "deepkeep",
    "version": "0.1.0",
    "description": "Checks prompts, shell commands, file reads, and MCP tool calls against your organization's DeepKeep policies. Configurable failure behavior controls whether actions proceed when validation fails.",
    "author": { "name": "DeepKeep" },
    "homepage": "https://deepkeep.ai",
    "repository": "https://github.com/Deepkeepai/deepkeep-integrations",
    "license": "Apache-2.0",
    "logo": "./assets/logo.svg",
    "keywords": [
        "security",
        "guardrails",
        "firewall",
        "policy",
        "ai-safety",
        "dlp",
        "compliance"
    ]
}
`)

// Plugin hooks run from the plugin root, so a relative command avoids quoting
// differences between POSIX shells and Windows PowerShell.
//
// failClosed is true on all four so a launcher or runtime failure blocks the
// action instead of silently disabling enforcement.
const hook = (event) => `            {
                "command": "./bin/deepkeep-hook.cmd ${event}",
                "timeout": 10,
                "failClosed": true
            }`

write("hooks/hooks.json", `{
    "version": 1,
    "hooks": {
        "beforeSubmitPrompt": [
${hook("prompt")}
        ],
        "beforeShellExecution": [
${hook("shell")}
        ],
        "beforeReadFile": [
${hook("file-read")}
        ],
        "beforeMCPExecution": [
${hook("mcp")}
        ]
    }
}
`)

write("assets/logo.svg", `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="DeepKeep">
    <title>DeepKeep</title>
    <path d="M32 4 8 13v18c0 14.2 9.8 24.9 24 29 14.2-4.1 24-14.8 24-29V13L32 4Z" fill="#0B1220"/>
    <path d="M32 9.6 13.2 16.6v14.6c0 11.5 7.8 20.3 18.8 23.9 11-3.6 18.8-12.4 18.8-23.9V16.6L32 9.6Z" fill="#1E6FFF"/>
    <path d="M22.5 31.8l6.6 6.6 12.4-12.4" fill="none" stroke="#FFFFFF" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
`)

write("commands/deepkeep-connect.md", `---
description: Configure DeepKeep guardrails — set the policy endpoint, API key, and fail mode.
---

Explain how to configure \`~/.deepkeep/config.json\` using the plugin README.
The user must enter their API key privately, outside the chat and agent tools.
Never ask for, read, write, display, or process the API key.
Remind the user to set directory permissions to \`0700\`, file permissions to
\`0600\`, and fully quit and reopen Cursor.
`)

write("README.md", `# DeepKeep guardrails for Cursor

Checks prompts, shell commands, file reads, and MCP tool calls against your
organization's DeepKeep policies before they reach the model or run on your
machine. The configured failure mode controls what happens if validation fails.

## What it does

The plugin registers four Cursor hooks. Each one sends the pending action to
your DeepKeep policy endpoint and either allows it or blocks it with an
explanation.

| Cursor hook | Checks |
| --- | --- |
| \`beforeSubmitPrompt\` | prompt text and attachment paths |
| \`beforeShellExecution\` | the command and working directory |
| \`beforeReadFile\` | the file path and contents |
| \`beforeMCPExecution\` | the MCP server, tool name, and tool input |

All four are configured \`failClosed\`, so if the plugin cannot run, the action
is blocked. If the policy service cannot be reached, \`failMode\` controls the
result and defaults to \`block\`. Set it to \`allow\` to let actions proceed unchecked.
The API truncates serialized payloads over 32,768 characters before inspection,
so a decision may not cover the full action.
Hook inputs over 5 MiB also follow \`failMode\` before payload parsing.

## Requirements

The plugin is free, but requires a paid DeepKeep API token to function.

No manual runtime install. The plugin ships a self-contained JavaScript bundle
and locates a runtime automatically, preferring \`node\` on your \`PATH\` and
falling back to the runtime shipped with Cursor.

Supported on macOS, Linux, and Windows.

## Configuration

Set the policy endpoint and API key in \`~/.deepkeep/config.json\`:

\`\`\`json
{
    "firewallUrl": "https://api.<tenant>.deepkeep.ai/api/v2/developer-agent/validate",
    "apiKey": "<your api key>",
    "failMode": "block"
}
\`\`\`

Create the directory with mode \`0700\` and the file with mode \`0600\`. Enter
the API key privately, outside Cursor chat and agent tools.

After configuring, fully quit Cursor (Cmd+Q / Alt+F4) and reopen it.

## Verifying it is working

\`\`\`bash
tail -f ~/.deepkeep/logs/hook.log
\`\`\`

Send a prompt or run a shell command in Cursor; you should see a decision
logged for the corresponding hook.

## Privacy

Prompt text, shell commands, file contents, and MCP tool inputs are sent to the
DeepKeep endpoint you configure for validation. Prompt attachments are sent as
paths, not contents. Hook inputs are limited to 5 MiB. Your API key is stored
locally in \`~/.deepkeep/config.json\` and is never written to logs.

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
`)

console.log(`[scaffold-plugin] wrote static plugin files under ${pluginRoot}`)
