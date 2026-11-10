import { existsSync, readFileSync } from "node:fs"

import { getDeviceId, readBearerFromFile } from "../lib/auth.js"
import { loadConfig } from "../lib/config.js"
import { validate } from "../lib/firewall-client.js"
import { CURSOR_HOOKS_FILE } from "../lib/paths.js"

interface CheckResult {
    name: string
    ok: boolean
    detail?: string
}

function fmt(c: CheckResult): string {
    const icon = c.ok ? "OK   " : "FAIL "
    return `[${icon}] ${c.name}${c.detail ? `  -  ${c.detail}` : ""}`
}

/**
 * Hooks are registered by the plugin itself, so a DeepKeep entry in the user's
 * own hooks file can only be a leftover from the retired installer. It would
 * double-validate every action, so surface it.
 */
function hasLegacyUserHooks(): boolean {
    if (!existsSync(CURSOR_HOOKS_FILE)) return false
    try {
        return /deepkeep/i.test(readFileSync(CURSOR_HOOKS_FILE, "utf8"))
    } catch {
        return false
    }
}

export async function runDoctor(): Promise<void> {
    const checks: CheckResult[] = []
    const cfg = loadConfig(getDeviceId())
    const hasCredentials = Boolean(cfg.apiKey || cfg.bearerToken || readBearerFromFile())

    checks.push({
        name: "policy endpoint",
        ok: cfg.firewallUrl.length > 0,
        detail: cfg.firewallUrl || "missing - set firewallUrl in ~/.deepkeep/config.json"
    })
    checks.push({
        name: "authentication",
        ok: hasCredentials,
        detail: hasCredentials ? "configured" : "missing - configure an API key or bearer token"
    })
    checks.push({
        name: "fail mode",
        ok: true,
        detail: cfg.failMode === "block" ? "block (recommended)" : "allow"
    })

    const legacy = hasLegacyUserHooks()
    checks.push({
        name: "no legacy hooks in ~/.cursor/hooks.json",
        ok: !legacy,
        detail: legacy
            ? `remove DeepKeep entries from ${CURSOR_HOOKS_FILE} - the plugin registers its own`
            : "clean"
    })

    if (cfg.firewallUrl.length > 0) {
        try {
            const res = await validate(cfg, {
                surface: "cursor",
                action: "before-prompt",
                payload: { prompt: "deepkeep-doctor probe", attachment_paths: [] },
                context: {
                    device_id: cfg.deviceId,
                    cwd: process.cwd(),
                    hostname: cfg.hostname,
                    os: cfg.os,
                    cli_version: cfg.cliVersion
                }
            })
            checks.push({
                name: "policy endpoint reachable",
                ok: true,
                detail: `violatePolicy=${res.violatePolicy}`
            })
        } catch (err) {
            checks.push({
                name: "policy endpoint reachable",
                ok: false,
                detail: err instanceof Error ? err.message : String(err)
            })
        }
    }

    for (const c of checks) process.stdout.write(fmt(c) + "\n")
    const failed = checks.some((c) => !c.ok)
    process.exit(failed ? 1 : 0)
}
