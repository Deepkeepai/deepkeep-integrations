import { readFileSync } from "node:fs"
import { join, resolve } from "node:path"
import { describe, expect, it } from "vitest"

describe("marketplace manifest", () => {
    it("points to the Cursor plugin manifest", () => {
        const repositoryRoot = resolve("../..")
        const marketplace = JSON.parse(readFileSync(join(repositoryRoot, ".cursor-plugin/marketplace.json"), "utf8"))
        expect(marketplace.plugins).toHaveLength(1)
        const entry = marketplace.plugins[0]
        const plugin = JSON.parse(readFileSync(join(repositoryRoot, entry.source, ".cursor-plugin/plugin.json"), "utf8"))
        expect(plugin.name).toBe(entry.name)
    })
})
