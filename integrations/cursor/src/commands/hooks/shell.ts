import type { BeforeShellExecutionInput, PermissionOutput } from "../../types/cursor-hooks.js"

import { helpers, resolveCwd, runHook } from "./runner.js"

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
