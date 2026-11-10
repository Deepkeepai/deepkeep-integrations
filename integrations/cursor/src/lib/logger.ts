import { appendFileSync, mkdirSync } from "node:fs"
import { dirname } from "node:path"

import { LOG_FILE } from "./paths.js"

let initialized = false

function ensureDir(): void {
    if (initialized) return
    try {
        mkdirSync(dirname(LOG_FILE), { recursive: true })
    } catch {
        /* ignore — logging is best-effort */
    }
    initialized = true
}

export function isDebug(): boolean {
    const v = process.env.DEEPKEEP_DEBUG
    return v === "1" || v === "true"
}

export function log(level: "info" | "warn" | "error" | "debug", msg: string, ctx?: Record<string, unknown>): void {
    if (level === "debug" && !isDebug()) return
    ensureDir()
    const line = JSON.stringify({
        ts: new Date().toISOString(),
        level,
        pid: process.pid,
        msg,
        ...(ctx ?? {})
    })
    try {
        appendFileSync(LOG_FILE, line + "\n", { encoding: "utf8" })
    } catch {
        /* logging must never throw */
    }
}
