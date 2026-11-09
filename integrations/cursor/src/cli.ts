import { Command } from "commander"

import { runDoctor } from "./commands/doctor.js"
import { runFileReadHook } from "./commands/hooks/file-read.js"
import { runMcpHook } from "./commands/hooks/mcp.js"
import { runPromptHook } from "./commands/hooks/prompt.js"
import { runShellHook } from "./commands/hooks/shell.js"
import { log } from "./lib/logger.js"

const program = new Command()
    .name("deepkeep-hook")
    .description("DeepKeep firewall guardrails for AI coding agents")
    .version("0.1.0")

program
    .command("doctor")
    .description("Verify configuration, auth, and firewall reachability")
    .action(async () => {
        await runDoctor()
    })

const hook = program.command("hook").description("Hook entrypoints invoked by Cursor")
hook.command("prompt").description("beforeSubmitPrompt").action(async () => runPromptHook())
hook.command("shell").description("beforeShellExecution").action(async () => runShellHook())
hook.command("file-read").description("beforeReadFile").action(async () => runFileReadHook())
hook.command("mcp").description("beforeMCPExecution").action(async () => runMcpHook())

program.parseAsync(process.argv).catch((err) => {
    log("error", "cli.fatal", { err: err instanceof Error ? err.message : String(err) })
    process.stderr.write(`deepkeep-hook: ${err instanceof Error ? err.message : String(err)}\n`)
    process.exit(1)
})
