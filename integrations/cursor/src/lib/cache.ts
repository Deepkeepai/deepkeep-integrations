import { createHash } from "node:crypto"
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs"
import { dirname } from "node:path"

import { CACHE_FILE } from "./paths.js"
import type { FirewallResponse } from "../types/firewall.js"

interface CacheEntry {
    response: FirewallResponse
    expiresAt: number
}

interface CacheFile {
    version: 1
    entries: Record<string, CacheEntry>
}

const MAX_ENTRIES = 500

export function makeKey(parts: Record<string, unknown>): string {
    return createHash("sha256").update(JSON.stringify(parts)).digest("hex")
}

let mem: CacheFile | null = null

function load(): CacheFile {
    if (mem) return mem
    if (!existsSync(CACHE_FILE)) {
        mem = { version: 1, entries: {} }
        return mem
    }
    try {
        const data = JSON.parse(readFileSync(CACHE_FILE, "utf8")) as CacheFile
        mem = data.version === 1 && data.entries ? data : { version: 1, entries: {} }
    } catch {
        mem = { version: 1, entries: {} }
    }
    return mem
}

function persist(): void {
    if (!mem) return
    try {
        mkdirSync(dirname(CACHE_FILE), { recursive: true })
        const tmp = `${CACHE_FILE}.tmp`
        writeFileSync(tmp, JSON.stringify(mem), { mode: 0o600 })
        renameSync(tmp, CACHE_FILE)
    } catch {
        /* cache is best-effort */
    }
}

export function cacheGet(key: string, ttlMs: number): FirewallResponse | null {
    if (ttlMs <= 0) return null
    const c = load()
    const entry = c.entries[key]
    if (!entry) return null
    if (Date.now() >= entry.expiresAt) {
        delete c.entries[key]
        return null
    }
    return entry.response
}

export function cacheSet(key: string, response: FirewallResponse, ttlMs: number): void {
    if (ttlMs <= 0) return
    const c = load()
    const ttl = response.decision_ttl_ms ?? ttlMs
    c.entries[key] = { response, expiresAt: Date.now() + ttl }

    const keys = Object.keys(c.entries)
    if (keys.length > MAX_ENTRIES) {
        keys
            .sort((a, b) => (c.entries[a]?.expiresAt ?? 0) - (c.entries[b]?.expiresAt ?? 0))
            .slice(0, keys.length - MAX_ENTRIES)
            .forEach((k) => delete c.entries[k])
    }
    persist()
}

export function resetCacheForTests(): void {
    mem = null
}
