import type { RuntimeConfig } from "./config.js"
import type {
    PermissionOutput,
    PromptOutput
} from "../types/cursor-hooks.js"
import type { FirewallResponse } from "../types/firewall.js"

const DEFAULT_BLOCK_MSG = "Blocked by DeepKeep firewall."
const DEFAULT_FAIL_BLOCK_MSG =
    "DeepKeep could not validate this action; blocking by policy. Contact your administrator."

export function explain(res: FirewallResponse): string {
    if (res.reason && res.reason.length > 0) return res.reason
    if (res.violations && res.violations.length > 0) {
        return `Policy violations: ${res.violations.join(", ")}`
    }
    return DEFAULT_BLOCK_MSG
}

export function toPromptOutput(res: FirewallResponse): PromptOutput {
    if (!res.violatePolicy) return { continue: true }
    return { continue: false, user_message: explain(res) }
}

export function toPermissionOutput(res: FirewallResponse): PermissionOutput {
    if (!res.violatePolicy) return { permission: "allow" }
    const msg = explain(res)
    return {
        permission: "deny",
        user_message: msg,
        agent_message: msg
    }
}

export function failOpenPrompt(): PromptOutput {
    return { continue: true }
}

export function failClosedPrompt(): PromptOutput {
    return { continue: false, user_message: DEFAULT_FAIL_BLOCK_MSG }
}

export function failOpenPermission(): PermissionOutput {
    return { permission: "allow" }
}

export function failClosedPermission(): PermissionOutput {
    return {
        permission: "deny",
        user_message: DEFAULT_FAIL_BLOCK_MSG,
        agent_message: DEFAULT_FAIL_BLOCK_MSG
    }
}

export function isFailClosed(cfg: RuntimeConfig): boolean {
    return cfg.failMode === "block"
}
