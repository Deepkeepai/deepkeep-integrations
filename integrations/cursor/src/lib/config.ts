import { existsSync, readFileSync } from "node:fs"
import { hostname, platform } from "node:os"

import { CONFIG_FILE } from "./paths.js"

export interface RuntimeConfig {
    firewallUrl: string
    apiKey: string | null
    bearerToken: string | null
    failMode: "allow" | "block"
    timeoutMs: number
    cacheTtlMs: number
    deviceId: string
    hostname: string
    os: string
    cliVersion: string
}

const PKG_VERSION = "0.1.0"
const FAIL_MODE_ALLOW = "allow"
const FAIL_MODE_BLOCK = "block"
const DEFAULT_REQUEST_TIMEOUT_MS = 2500
const MAX_REQUEST_TIMEOUT_MS = 5000

function readFile(): Record<string, unknown> {
    if (!existsSync(CONFIG_FILE)) return {}
    try {
        const value: unknown = JSON.parse(readFileSync(CONFIG_FILE, "utf8").replace(/^\uFEFF/, ""))
        return value && typeof value === "object" && !Array.isArray(value)
            ? value as Record<string, unknown>
            : { failMode: FAIL_MODE_BLOCK }
    } catch {
        return { failMode: FAIL_MODE_BLOCK }
    }
}

function pickString(env: string | undefined, fileVal: unknown): string | null {
    if (typeof env === "string" && env.length > 0) return env
    if (typeof fileVal === "string" && fileVal.length > 0) return fileVal
    return null
}

function pickNumber(env: string | undefined, fileVal: unknown, fallback: number): number {
    const fromEnv = env != null ? Number(env) : NaN
    if (Number.isFinite(fromEnv) && fromEnv >= 0) return fromEnv
    if (typeof fileVal === "number" && Number.isFinite(fileVal) && fileVal >= 0) return fileVal
    return fallback
}

function pickFailMode(env: string | undefined, fileVal: unknown): "allow" | "block" {
    const v = (typeof fileVal === "string" ? fileVal : env ?? "").toLowerCase()
    return v === FAIL_MODE_ALLOW ? FAIL_MODE_ALLOW : FAIL_MODE_BLOCK
}

let cached: RuntimeConfig | null = null

export function loadConfig(deviceId: string): RuntimeConfig {
    if (cached) return cached
    const f = readFile()

    const firewallUrl = pickString(typeof f.firewallUrl === "string" ? f.firewallUrl : undefined, process.env.DEEPKEEP_FIREWALL_URL)
    const apiKey = pickString(typeof f.apiKey === "string" ? f.apiKey : undefined, process.env.DEEPKEEP_API_KEY)
    const configuredTimeoutMs = pickNumber(process.env.DEEPKEEP_TIMEOUT_MS, f.timeoutMs, DEFAULT_REQUEST_TIMEOUT_MS)
    const timeoutMs = configuredTimeoutMs >= 1
        ? Math.min(Math.floor(configuredTimeoutMs), MAX_REQUEST_TIMEOUT_MS)
        : DEFAULT_REQUEST_TIMEOUT_MS

    if (!firewallUrl) {
        process.stderr.write(
            `[deepkeep] ERROR: DEEPKEEP_FIREWALL_URL not configured.\n` +
            `Set it via environment variable or ~/.deepkeep/config.json\n` +
            `Example: https://api.<tenant>.deepkeep.ai/api/v2/developer-agent/validate\n`
        )
    }

    cached = {
        firewallUrl: firewallUrl ?? "",
        apiKey,
        bearerToken: pickString(typeof f.bearerToken === "string" ? f.bearerToken : undefined, process.env.DEEPKEEP_BEARER_TOKEN),
        failMode: pickFailMode(process.env.DEEPKEEP_FAIL_MODE, f.failMode),
        timeoutMs,
        cacheTtlMs: pickNumber(process.env.DEEPKEEP_CACHE_TTL_MS, f.cacheTtlMs, 300_000),
        deviceId,
        hostname: hostname(),
        os: platform(),
        cliVersion: PKG_VERSION
    }

    return cached
}

export function resetConfigForTests(): void {
    cached = null
}

/**
 * Returns true when both firewallUrl and apiKey are resolvable from either
 * the runtime environment or ~/.deepkeep/config.json. Used by `init` to decide
 * whether to prompt the user. No side effects.
 */
export function isConfigured(): boolean {
    const f = readFile()
    const firewallUrl = pickString(typeof f.firewallUrl === "string" ? f.firewallUrl : undefined, process.env.DEEPKEEP_FIREWALL_URL)
    const apiKey = pickString(typeof f.apiKey === "string" ? f.apiKey : undefined, process.env.DEEPKEEP_API_KEY)
    return Boolean(firewallUrl && apiKey)
}
