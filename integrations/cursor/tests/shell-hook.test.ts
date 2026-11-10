import { afterEach, beforeEach, describe, expect, it } from "vitest"

import { resolveCwd } from "../src/commands/hooks/runner.js"

const ENV_KEY = "CURSOR_PROJECT_DIR"

describe("resolveCwd", () => {
    let originalEnv: string | undefined

    beforeEach(() => {
        originalEnv = process.env[ENV_KEY]
        delete process.env[ENV_KEY]
    })

    afterEach(() => {
        if (originalEnv === undefined) {
            delete process.env[ENV_KEY]
        } else {
            process.env[ENV_KEY] = originalEnv
        }
    })

    it("uses raw.cwd when present", () => {
        expect(resolveCwd({ cwd: "/from/raw", workspace_roots: ["/from/roots"] })).toBe("/from/raw")
    })

    it("falls back to workspace_roots[0] when cwd is empty string", () => {
        // Empirical: Cursor sometimes sends ``cwd: ""`` even though docs say
        // it's populated. The Prompts page used to render ``(unset)`` for these.
        expect(resolveCwd({ cwd: "", workspace_roots: ["/from/roots"] })).toBe("/from/roots")
    })

    it("falls back to workspace_roots[0] when cwd is missing", () => {
        expect(resolveCwd({ workspace_roots: ["/only/roots"] })).toBe("/only/roots")
    })

    it("ignores non-string entries in workspace_roots", () => {
        expect(
            resolveCwd({ workspace_roots: [42, null, undefined, "/finally/here"] as unknown[] })
        ).toBe("/finally/here")
    })

    it("falls back to CURSOR_PROJECT_DIR env var when neither cwd nor roots resolve", () => {
        process.env[ENV_KEY] = "/from/env"
        expect(resolveCwd({})).toBe("/from/env")
    })

    it("ignores empty CURSOR_PROJECT_DIR env var", () => {
        process.env[ENV_KEY] = ""
        expect(resolveCwd({})).toBeUndefined()
    })

    it("returns undefined when nothing is set", () => {
        expect(resolveCwd({ cwd: "", workspace_roots: [] })).toBeUndefined()
    })

    it("priority is cwd > workspace_roots > env", () => {
        process.env[ENV_KEY] = "/env-loses"
        expect(
            resolveCwd({ cwd: "/cwd-wins", workspace_roots: ["/roots-loses"] })
        ).toBe("/cwd-wins")
    })

    it("priority is workspace_roots > env when cwd is empty", () => {
        process.env[ENV_KEY] = "/env-loses"
        expect(
            resolveCwd({ cwd: "", workspace_roots: ["/roots-wins"] })
        ).toBe("/roots-wins")
    })
})
