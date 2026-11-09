import { cpSync, mkdtempSync, readFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { spawnSync } from "node:child_process"
import { afterAll, describe, expect, it } from "vitest"

const home = mkdtempSync(join(tmpdir(), "deepkeep hook test "))
const plugin = join(home, "plugin with spaces")
cpSync("cursor-plugin", plugin, { recursive: true })

afterAll(() => rmSync(home, { recursive: true, force: true }))

describe.skipIf(process.platform === "win32")("POSIX hook launcher", () => {
    it.each([
        ["beforeSubmitPrompt", { prompt: "test", attachments: [] }, { continue: true }],
        ["beforeShellExecution", { command: "echo test" }, { permission: "allow" }],
        ["beforeReadFile", { file_path: "/test", content: "test" }, { permission: "allow" }],
        ["beforeMCPExecution", { tool_name: "test", tool_input: "{}" }, { permission: "allow" }]
    ])("runs %s from a path with spaces", (event, input, expected) => {
        const hooks = JSON.parse(readFileSync(join(plugin, "hooks/hooks.json"), "utf8"))
        const command = hooks.hooks[event][0].command
        const result = spawnSync("/bin/sh", ["-c", command], {
            cwd: plugin,
            input: JSON.stringify(input),
            encoding: "utf8",
            timeout: 10000,
            env: {
                ...process.env,
                HOME: home,
                DEEPKEEP_NODE: process.execPath,
                DEEPKEEP_FAIL_MODE: "allow",
                DEEPKEEP_FIREWALL_URL: "",
                DEEPKEEP_API_KEY: "",
                DEEPKEEP_BEARER_TOKEN: ""
            }
        })
        expect(result.status).toBe(0)
        expect(JSON.parse(result.stdout)).toMatchObject(expected)
    })
})

describe.skipIf(process.platform !== "win32")("Windows hook launcher", () => {
    it("runs a prompt hook from a path with spaces", () => {
        const hooks = JSON.parse(readFileSync(join(plugin, "hooks/hooks.json"), "utf8"))
        const command = hooks.hooks.beforeSubmitPrompt[0].command
        const result = spawnSync("powershell.exe", ["-NoLogo", "-NoProfile", "-NonInteractive", "-Command", `$input | & { ${command} }`], {
            cwd: plugin,
            input: JSON.stringify({ prompt: "test", attachments: [] }),
            encoding: "utf8",
            timeout: 10000,
            env: {
                ...process.env,
                USERPROFILE: home,
                HOME: home,
                DEEPKEEP_NODE: process.execPath,
                DEEPKEEP_FAIL_MODE: "allow",
                DEEPKEEP_FIREWALL_URL: "",
                DEEPKEEP_API_KEY: "",
                DEEPKEEP_BEARER_TOKEN: ""
            }
        })
        expect(result.status).toBe(0)
        expect(JSON.parse(result.stdout)).toMatchObject({ continue: true })
    })
})
