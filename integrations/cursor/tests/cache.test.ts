import { mkdtempSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

let tempHome: string

beforeEach(() => {
    tempHome = mkdtempSync(join(tmpdir(), "dk-cache-"))
    vi.resetModules()
    process.env.HOME = tempHome
})

afterEach(() => {
    rmSync(tempHome, { recursive: true, force: true })
    vi.unstubAllEnvs()
})

describe("cache", () => {
    it("returns null on miss and stored value within TTL", async () => {
        const { cacheGet, cacheSet, makeKey, resetCacheForTests } = await import("../src/lib/cache.js")
        resetCacheForTests()

        const key = makeKey({ a: 1 })
        expect(cacheGet(key, 60_000)).toBeNull()
        cacheSet(key, { violatePolicy: false, content: "" }, 60_000)
        expect(cacheGet(key, 60_000)).toEqual({ violatePolicy: false, content: "" })
    })

    it("disables when ttl is 0", async () => {
        const { cacheGet, cacheSet, makeKey, resetCacheForTests } = await import("../src/lib/cache.js")
        resetCacheForTests()

        const key = makeKey({ a: 2 })
        cacheSet(key, { violatePolicy: true, content: "" }, 0)
        expect(cacheGet(key, 0)).toBeNull()
    })

    it("respects decision_ttl_ms from response", async () => {
        const { cacheGet, cacheSet, makeKey, resetCacheForTests } = await import("../src/lib/cache.js")
        resetCacheForTests()

        const key = makeKey({ a: 3 })
        cacheSet(key, { violatePolicy: false, content: "", decision_ttl_ms: 1 }, 60_000)
        await new Promise((r) => setTimeout(r, 10))
        expect(cacheGet(key, 60_000)).toBeNull()
    })
})
