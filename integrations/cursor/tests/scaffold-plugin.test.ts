import { cpSync, existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { spawnSync } from "node:child_process"
import { describe, expect, it } from "vitest"

describe("plugin scaffold", () => {
    it("creates managed files when the plugin directory is missing", () => {
        const root = mkdtempSync(join(tmpdir(), "deepkeep-scaffold-"))
        try {
            mkdirSync(join(root, "scripts"))
            for (const file of ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES", "scripts/scaffold-plugin.mjs"]) {
                cpSync(file, join(root, file))
            }
            const result = spawnSync(process.execPath, [join(root, "scripts/scaffold-plugin.mjs")], { encoding: "utf8" })
            expect(result.status).toBe(0)
            expect(existsSync(join(root, "cursor-plugin/LICENSE"))).toBe(true)
            expect(JSON.parse(readFileSync(join(root, "cursor-plugin/package.json"), "utf8"))).toEqual({ type: "module" })
        } finally {
            rmSync(root, { recursive: true, force: true })
        }
    })
})
