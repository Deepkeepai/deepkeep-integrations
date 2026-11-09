import type { BeforeShellExecutionInput, PermissionOutput } from "../../types/cursor-hooks.js"

import { helpers, runHook } from "./runner.js"

/**
 * Resolve the working directory for a shell hook with the documented
 * Cursor fallback chain:
 *
 *   1. ``cwd`` — top-level field per the official ``beforeShellExecution``
 *      schema. Empirically this is sometimes empty; the docs don't say
 *      under what conditions, and we don't want the api / Prompts page
 *      to render a meaningless ``(unset)``.
 *   2. ``workspace_roots[0]`` — also a top-level field on every Cursor
 *      hook (part of the 8-field common envelope). When the agent has
 *      a single repo open this is the same as ``cwd``; when multiple
 *      roots are open, the first one is the active workspace.
 *   3. ``CURSOR_PROJECT_DIR`` env var — Cursor sets this on every hook
 *      invocation per the docs, so it's the most reliable last resort.
 *
 * Returns ``undefined`` only when none of those resolve, in which case
 * the api stamps an empty string and the UI is honest about not knowing.
 */
export function resolveCwd(raw: Record<string, unknown>): string | undefined {
    if (typeof raw.cwd === "string" && raw.cwd.length > 0) return raw.cwd
    if (Array.isArray(raw.workspace_roots)) {
        // Walk the list rather than only checking ``[0]``: in practice the
        // first entry is always a string, but if a future Cursor version
        // ever interleaves nulls or routes objects through here, we still
        // pick up a usable path instead of falling all the way through
        // to the env var.
        for (const candidate of raw.workspace_roots) {
            if (typeof candidate === "string" && candidate.length > 0) {
                return candidate
            }
        }
    }
    const envDir = process.env.CURSOR_PROJECT_DIR
    if (typeof envDir === "string" && envDir.length > 0) return envDir
    return undefined
}

export async function runShellHook(): Promise<void> {
    await runHook<BeforeShellExecutionInput, PermissionOutput>({
        action: "before-shell",
        parseInput: (raw) => {
            if (!raw || typeof raw !== "object") return null
            const r = raw as Record<string, unknown>
            if (typeof r.command !== "string") return null
            return {
                command: r.command,
                cwd: resolveCwd(r),
                sandbox: typeof r.sandbox === "boolean" ? r.sandbox : undefined
            }
        },
        buildPayload: (i) => ({ command: i.command, cwd: i.cwd, sandbox: i.sandbox }),
        buildContext: (i, base) => ({ ...base, cwd: i.cwd ?? base.cwd }),
        onFailOpen: () => helpers.failOpenPermission(),
        onFailClosed: () => helpers.failClosedPermission(),
        mapResponse: (res) => helpers.toPermissionOutput(res)
    })
}
