import type { BeforeMCPExecutionInput, PermissionOutput } from "../../types/cursor-hooks.js"

import { helpers, runHook } from "./runner.js"

export async function runMcpHook(): Promise<void> {
    await runHook<BeforeMCPExecutionInput, PermissionOutput>({
        action: "before-mcp",
        parseInput: (raw) => {
            if (!raw || typeof raw !== "object") return null
            const r = raw as Record<string, unknown>
            if (typeof r.tool_name !== "string" || r.tool_input == null) return null
            return {
                tool_name: r.tool_name,
                tool_input: r.tool_input,
                url: typeof r.url === "string" ? r.url : undefined,
                command: typeof r.command === "string" ? r.command : undefined
            }
        },
        buildPayload: (i) => ({
            tool_name: i.tool_name,
            tool_input: i.tool_input,
            server_url: i.url,
            server_command: i.command
        }),
        onFailOpen: () => helpers.failOpenPermission(),
        onFailClosed: () => helpers.failClosedPermission(),
        mapResponse: (res) => helpers.toPermissionOutput(res)
    })
}
