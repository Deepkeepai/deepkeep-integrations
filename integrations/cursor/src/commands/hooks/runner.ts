import { getDeviceId } from "../../lib/auth.js"
import { loadConfig } from "../../lib/config.js"
import {
    failClosedPermission,
    failClosedPrompt,
    failOpenPermission,
    failOpenPrompt,
    isFailClosed,
    toPermissionOutput,
    toPromptOutput
} from "../../lib/decision.js"
import { RedactionUnsupportedError, validate } from "../../lib/firewall-client.js"
import { log } from "../../lib/logger.js"
import { parseJson, readStdin } from "../../lib/stdin.js"
import type { PermissionOutput, PromptOutput } from "../../types/cursor-hooks.js"
import type { Action, FirewallContext, FirewallRequest, FirewallResponse } from "../../types/firewall.js"

export interface HookSpec<TInput, TOutput extends PromptOutput | PermissionOutput> {
    action: Action
    parseInput: (raw: unknown) => TInput | null
    buildPayload: (input: TInput) => Record<string, unknown>
    buildContext?: (input: TInput, base: FirewallContext) => FirewallContext
    onFailOpen: () => TOutput
    onFailClosed: () => TOutput
    mapResponse: (res: FirewallResponse) => TOutput
}

function emit(out: PromptOutput | PermissionOutput): void {
    process.stdout.write(JSON.stringify(out))
}

function stringField(obj: Record<string, unknown>, ...keys: string[]): string | undefined {
    for (const key of keys) {
        const value = obj[key]
        if (typeof value === "string" && value.trim().length > 0) return value
    }
    return undefined
}

export function resolveCwd(raw: Record<string, unknown>): string | undefined {
    const cwd = stringField(raw, "cwd")
    if (cwd) return cwd
    if (Array.isArray(raw.workspace_roots)) {
        const root = raw.workspace_roots.find((value): value is string =>
            typeof value === "string" && value.trim().length > 0
        )
        if (root) return root
    }
    return process.env.CURSOR_PROJECT_DIR?.trim() ? process.env.CURSOR_PROJECT_DIR : undefined
}

function contextFromRaw(raw: unknown): Pick<FirewallContext, "cwd" | "session_id" | "conversation_id" | "generation_id" | "user_email"> {
    if (!raw || typeof raw !== "object") return {}
    const record = raw as Record<string, unknown>
    const nested = record.context && typeof record.context === "object"
        ? record.context as Record<string, unknown>
        : {}

    return {
        cwd: resolveCwd(record),
        // Cursor hook payloads may evolve; accept both snake_case and
        // camelCase, either top-level or under a `context` object. The API
        // stores both values separately in firewall_event.additional_data.
        session_id: stringField(record, "session_id", "sessionId")
            ?? stringField(nested, "session_id", "sessionId"),
        conversation_id: stringField(record, "conversation_id", "conversationId")
            ?? stringField(nested, "conversation_id", "conversationId"),
        // generation_id groups all hooks from a single agent turn/generation.
        // This allows correlating before-prompt, before-shell, before-mcp, etc.
        // that were triggered by the same user prompt.
        generation_id: stringField(record, "generation_id", "generationId")
            ?? stringField(nested, "generation_id", "generationId"),
        // user_email identifies the Cursor user (for tenant policy attribution).
        // Cursor may provide this in the hook payload or via environment variable.
        user_email: stringField(record, "user_email", "userEmail", "email")
            ?? stringField(nested, "user_email", "userEmail", "email")
            ?? process.env.CURSOR_USER_EMAIL
    }
}

export async function runHook<TInput, TOutput extends PromptOutput | PermissionOutput>(
    spec: HookSpec<TInput, TOutput>
): Promise<void> {
    const cfg = loadConfig(getDeviceId())
    const startedAt = Date.now()

    let input: TInput | null = null
    let rawContext: Pick<FirewallContext, "cwd" | "session_id" | "conversation_id" | "generation_id" | "user_email"> = {}
    try {
        const raw = await readStdin()
        const parsed = parseJson(raw)
        rawContext = contextFromRaw(parsed)
        input = spec.parseInput(parsed)
    } catch (err) {
        log("warn", "hook.stdin error", { action: spec.action, err: String(err) })
    }

    if (input == null) {
        log("warn", "hook.input invalid", { action: spec.action })
        emit(isFailClosed(cfg) ? spec.onFailClosed() : spec.onFailOpen())
        return
    }

    const baseCtx: FirewallContext = {
        device_id: cfg.deviceId,
        ...rawContext,
        hostname: cfg.hostname,
        os: cfg.os,
        cli_version: cfg.cliVersion
    }
    let ctx: FirewallContext
    let payload: Record<string, unknown>
    try {
        ctx = spec.buildContext ? spec.buildContext(input, baseCtx) : baseCtx
        payload = spec.buildPayload(input)
    } catch {
        log("warn", "hook.input invalid", { action: spec.action })
        emit(isFailClosed(cfg) ? spec.onFailClosed() : spec.onFailOpen())
        return
    }
    const req: FirewallRequest = { surface: "cursor", action: spec.action, payload, context: ctx }

    try {
        const res = await validate(cfg, req)
        log("info", "hook.decision", {
            action: spec.action,
            violatePolicy: res.violatePolicy,
            elapsed_ms: Date.now() - startedAt
        })
        emit(spec.mapResponse(res))
    } catch (err) {
        log("warn", "hook.firewall error", {
            action: spec.action,
            elapsed_ms: Date.now() - startedAt,
            err: err instanceof Error ? err.message : String(err)
        })
        emit(err instanceof RedactionUnsupportedError || isFailClosed(cfg) ? spec.onFailClosed() : spec.onFailOpen())
    }
}

export const helpers = {
    failOpenPermission,
    failClosedPermission,
    failOpenPrompt,
    failClosedPrompt,
    toPermissionOutput,
    toPromptOutput
}
