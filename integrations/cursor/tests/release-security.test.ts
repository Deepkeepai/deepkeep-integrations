import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import axios, { AxiosError } from "axios"

import { loadConfig, resetConfigForTests, type RuntimeConfig } from "../src/lib/config.js"
import { RedactionUnsupportedError, validate } from "../src/lib/firewall-client.js"
import { runHook } from "../src/commands/hooks/runner.js"
import { runFileReadHook } from "../src/commands/hooks/file-read.js"
import { runPromptHook } from "../src/commands/hooks/prompt.js"
import { runMcpHook } from "../src/commands/hooks/mcp.js"
import { runShellHook } from "../src/commands/hooks/shell.js"
import * as stdin from "../src/lib/stdin.js"
import * as config from "../src/lib/config.js"
import * as firewall from "../src/lib/firewall-client.js"
import type { FirewallRequest } from "../src/types/firewall.js"
import type { PromptOutput } from "../src/types/cursor-hooks.js"

vi.mock("node:fs", async (importOriginal) => {
    const actual = await importOriginal<typeof import("node:fs")>()
    return { ...actual, existsSync: vi.fn(actual.existsSync), readFileSync: vi.fn(actual.readFileSync) }
})

import * as fs from "node:fs"

const BLOCK_CONFIG: RuntimeConfig = {
    firewallUrl: "https://example.com/validate", apiKey: "test", bearerToken: null,
    failMode: "block", timeoutMs: 1000, cacheTtlMs: 300000,
    deviceId: "device", hostname: "host", os: "linux", cliVersion: "test"
}
const REQUEST: FirewallRequest = {
    surface: "cursor", action: "before-prompt", payload: {}, context: { device_id: "device" }
}

describe("release security", () => {
    beforeEach(() => resetConfigForTests())
    afterEach(() => {
        vi.restoreAllMocks()
        vi.unstubAllEnvs()
        resetConfigForTests()
    })

    it.each([
        ["prompt", runPromptHook, { prompt: "test", attachments: [] }],
        ["shell", runShellHook, { command: "echo test" }],
        ["file", runFileReadHook, { file_path: "/file", content: "test" }],
        ["mcp", runMcpHook, { tool_name: "test", tool_input: {} }]
    ])("sends the workspace directory for %s hooks", async (_name, hook, input) => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ ...input, workspace_roots: ["/workspace"] }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await hook()
        expect(request.mock.calls[0]?.[1].context.cwd).toBe("/workspace")
    })

    it("does not report the plugin directory when the workspace is unknown", async () => {
        vi.stubEnv("CURSOR_PROJECT_DIR", "")
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ prompt: "test" }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runPromptHook()
        expect(request.mock.calls[0]?.[1].context.cwd).toBeUndefined()
    })

    it("parses hook JSON with a leading UTF-8 BOM", () => {
        expect(stdin.parseJson('\uFEFF{"prompt":"test"}')).toEqual({ prompt: "test" })
    })

    it("does not let environment variables override configured credentials or fail mode", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockReturnValue(JSON.stringify({
            firewallUrl: BLOCK_CONFIG.firewallUrl, apiKey: "configured", failMode: "block"
        }))
        vi.stubEnv("DEEPKEEP_FIREWALL_URL", "https://other.example/validate")
        vi.stubEnv("DEEPKEEP_API_KEY", "other")
        vi.stubEnv("DEEPKEEP_FAIL_MODE", "allow")
        expect(loadConfig("device")).toMatchObject({
            firewallUrl: BLOCK_CONFIG.firewallUrl, apiKey: "configured", failMode: "block"
        })
    })

    it("defaults to block when the config file is missing", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(false)
        vi.stubEnv("DEEPKEEP_FAIL_MODE", "")
        expect(loadConfig("device").failMode).toBe("block")
    })

    it.each(["invalid json", "null", "[]"])("blocks on invalid configuration: %s", (contents) => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockReturnValue(contents)
        vi.stubEnv("DEEPKEEP_FAIL_MODE", "allow")
        expect(loadConfig("device").failMode).toBe("block")
    })

    it("blocks when the config file cannot be read", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockImplementation(() => { throw new Error("unreadable") })
        vi.stubEnv("DEEPKEEP_FAIL_MODE", "allow")
        expect(loadConfig("device").failMode).toBe("block")
    })

    it("honors an explicitly configured allow mode", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockReturnValue(JSON.stringify({ failMode: "allow" }))
        expect(loadConfig("device").failMode).toBe("allow")
    })

    it("reads configuration with a leading UTF-8 BOM", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockReturnValue('\uFEFF{"failMode":"allow"}')
        expect(loadConfig("device").failMode).toBe("allow")
    })

    it.each([
        [30000, 5000],
        [5000, 5000],
        [1200, 1200],
        [0, 2500]
    ])("bounds timeoutMs %s to %s", (configured, expected) => {
        vi.spyOn(fs, "existsSync").mockReturnValue(true)
        vi.spyOn(fs, "readFileSync").mockReturnValue(JSON.stringify({ timeoutMs: configured }))
        vi.stubEnv("DEEPKEEP_TIMEOUT_MS", "")
        // An unset environment value must not override the file setting.
        delete process.env.DEEPKEEP_TIMEOUT_MS
        expect(loadConfig("device").timeoutMs).toBe(expected)
    })

    it("bounds an environment timeout", () => {
        vi.spyOn(fs, "existsSync").mockReturnValue(false)
        vi.stubEnv("DEEPKEEP_TIMEOUT_MS", "30000")
        expect(loadConfig("device").timeoutMs).toBe(5000)
    })

    it.each(["allow", "block"] as const)("uses %s fail mode when the request deadline expires", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode, timeoutMs: 20 })
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ prompt: "test" }))
        vi.spyOn(axios, "post").mockImplementation((_url, _data, options) => new Promise((_resolve, reject) => {
            options?.signal?.addEventListener?.("abort", () => reject(new AxiosError("timeout", "ERR_CANCELED")))
        }))
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runPromptHook()
        expect(JSON.parse(String(output.mock.lastCall?.[0]))).toMatchObject({ continue: mode === "allow" })
    })

    it.each(["block", "allow"] as const)("handles invalid input using fail mode %s", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode })
        vi.spyOn(stdin, "readStdin").mockRejectedValue(new Error("input too large"))
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runHook<unknown, PromptOutput>({
            action: "before-prompt", parseInput: () => null, buildPayload: () => ({}),
            onFailOpen: () => ({ continue: true }), onFailClosed: () => ({ continue: false }),
            mapResponse: () => ({ continue: true })
        })
        expect(JSON.parse(String(output.mock.calls[0]?.[0]))).toEqual({ continue: mode === "allow" })
    })

    it("sends the entire file content to the firewall", async () => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        const content = "a".repeat(8 * 1024) + "secret-at-the-end"
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ file_path: "/file", content }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runFileReadHook()
        expect(request.mock.calls[0]?.[1].payload).toMatchObject({ content, content_truncated: false })
    })

    it("sends file payloads larger than 16 KiB to the API", async () => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        const content = "a".repeat(64 * 1024) + "secret-at-the-end"
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ file_path: "/file", content }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runFileReadHook()
        expect(request.mock.calls[0]?.[1].payload).toMatchObject({ content })
    })

    it.each(["allow", "block"] as const)("uses %s fail mode when file content is missing", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode })
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ file_path: "/file" }))
        const request = vi.spyOn(firewall, "validate")
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runFileReadHook()
        expect(request).not.toHaveBeenCalled()
        expect(JSON.parse(String(output.mock.calls[0]?.[0]))).toMatchObject({
            permission: mode === "block" ? "deny" : "allow"
        })
    })

    it("validates an empty file without treating it as missing content", async () => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ file_path: "/file", content: "" }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runFileReadHook()
        expect(request.mock.calls[0]?.[1].payload).toMatchObject({ content: "" })
    })

    it.each(["file", "rule"])("sends prompt attachment paths of type %s", async (type) => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({
            prompt: "test", attachments: [{ type, file_path: "/file" }]
        }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runPromptHook()
        expect(request.mock.calls[0]?.[1].payload).toMatchObject({ attachment_paths: ["/file"] })
        expect(JSON.parse(String(output.mock.calls[0]?.[0]))).toMatchObject({ continue: true })
    })

    it("validates prompts without attachments", async () => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ prompt: "test", attachments: [] }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runPromptHook()
        expect(request).toHaveBeenCalledOnce()
    })

    it.each(["allow", "block"] as const)("uses %s fail mode for malformed attachments", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode })
        const input = vi.spyOn(stdin, "readStdin")
        const request = vi.spyOn(firewall, "validate")
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        for (const attachment of [null, 42, {}, { file_path: 42 }]) {
            input.mockResolvedValue(JSON.stringify({ prompt: "test", attachments: [attachment] }))
            await runPromptHook()
            expect(JSON.parse(String(output.mock.lastCall?.[0]))).toMatchObject({ continue: mode === "allow" })
            input.mockResolvedValue(JSON.stringify({ file_path: "/file", content: "", attachments: [attachment] }))
            await runFileReadHook()
            expect(JSON.parse(String(output.mock.lastCall?.[0]))).toMatchObject({
                permission: mode === "allow" ? "allow" : "deny"
            })
        }
        expect(request).not.toHaveBeenCalled()
    })

    it.each(["allow", "block"] as const)("uses %s fail mode when building the payload fails", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode })
        vi.spyOn(stdin, "readStdin").mockResolvedValue("{}")
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runHook<unknown, PromptOutput>({
            action: "before-prompt", parseInput: () => ({}), buildPayload: () => { throw new Error("invalid") },
            onFailOpen: () => ({ continue: true }), onFailClosed: () => ({ continue: false }),
            mapResponse: () => ({ continue: true })
        })
        expect(JSON.parse(String(output.mock.lastCall?.[0]))).toEqual({ continue: mode === "allow" })
    })

    it.each(["allow", "block"] as const)("uses %s fail mode for missing MCP input", async (mode) => {
        vi.spyOn(config, "loadConfig").mockReturnValue({ ...BLOCK_CONFIG, failMode: mode })
        const input = vi.spyOn(stdin, "readStdin")
        const request = vi.spyOn(firewall, "validate")
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        for (const payload of [{ tool_name: "tool" }, { tool_name: "tool", tool_input: null }]) {
            input.mockResolvedValue(JSON.stringify(payload))
            await runMcpHook()
            expect(JSON.parse(String(output.mock.lastCall?.[0]))).toMatchObject({
                permission: mode === "allow" ? "allow" : "deny"
            })
        }
        expect(request).not.toHaveBeenCalled()
    })

    it("validates MCP calls with empty arguments", async () => {
        vi.spyOn(config, "loadConfig").mockReturnValue(BLOCK_CONFIG)
        vi.spyOn(stdin, "readStdin").mockResolvedValue(JSON.stringify({ tool_name: "tool", tool_input: "{}" }))
        const request = vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        await runMcpHook()
        expect(request.mock.calls[0]?.[1].payload).toMatchObject({ tool_input: "{}" })
    })

    it("never sends credentials to an insecure or credentialed URL", async () => {
        const post = vi.spyOn(axios, "post")
        for (const firewallUrl of ["http://example.com", "https://user:pass@example.com", "not-a-url"]) {
            await expect(validate({ ...BLOCK_CONFIG, firewallUrl }, REQUEST)).rejects.toThrow("HTTPS")
        }
        expect(post).not.toHaveBeenCalled()
    })

    it("rejects redaction responses rather than silently allowing the original input", async () => {
        vi.spyOn(axios, "post").mockResolvedValue({ data: { violatePolicy: false, redacted_text: "redacted" } })
        await expect(validate(BLOCK_CONFIG, REQUEST)).rejects.toBeInstanceOf(RedactionUnsupportedError)
    })

    it.each([[401, "authentication rejected"], [429, "rate limited"]])("reports HTTP %s as %s", async (status, message) => {
        const error = new AxiosError("request failed", "ERR_BAD_RESPONSE")
        error.response = { status, statusText: "", headers: {}, config: {} as never, data: {} }
        vi.spyOn(axios, "post").mockRejectedValue(error)
        await expect(validate(BLOCK_CONFIG, REQUEST)).rejects.toThrow(message)
    })
})
