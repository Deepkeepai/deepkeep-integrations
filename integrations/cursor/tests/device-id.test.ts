import { execFile } from "node:child_process"
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { promisify } from "node:util"
import ts from "typescript"
import { describe, expect, it } from "vitest"

const execFileAsync = promisify(execFile)
const CONCURRENT_HOOKS = 12

describe("device identity", () => {
    it("publishes one complete ID when hooks start concurrently", async () => {
        const home = mkdtempSync(join(tmpdir(), "deepkeep-device-"))
        try {
            const modulePath = join(home, "auth.js")
            for (const name of ["auth", "paths"]) {
                const source = readFileSync(join("src/lib", `${name}.ts`), "utf8")
                const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } })
                writeFileSync(join(home, `${name}.js`), compiled.outputText)
            }
            const code = `process.stdout.write(require(${JSON.stringify(modulePath)}).getDeviceId())`
            const results = await Promise.all(Array.from({ length: CONCURRENT_HOOKS }, () =>
                execFileAsync(process.execPath, ["-e", code], {
                    env: { ...process.env, HOME: home, USERPROFILE: home }
                })
            ))
            const storedId = readFileSync(join(home, ".deepkeep/device_id"), "utf8")
            expect(storedId).toMatch(/^[a-f0-9]{32}$/)
            expect(results.map(({ stdout }) => stdout)).toEqual(Array(CONCURRENT_HOOKS).fill(storedId))
        } finally {
            rmSync(home, { recursive: true, force: true })
        }
    })
})
