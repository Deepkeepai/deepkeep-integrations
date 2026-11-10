import { z } from "zod"

export type Surface = "cursor"
export type Action =
    | "before-prompt"
    | "before-shell"
    | "before-file-read"
    | "before-mcp"
    | "after-prompt"
    | "after-shell"
    | "after-file-read"
    | "after-mcp"

export interface FirewallContext {
    cwd?: string
    repo?: string
    workspace_roots?: string[]
    device_id: string
    session_id?: string
    conversation_id?: string
    generation_id?: string
    user_email?: string
    hostname?: string
    os?: string
    cli_version?: string
}

export interface FirewallRequest {
    surface: Surface
    action: Action
    payload: Record<string, unknown>
    context: FirewallContext
}

export const FirewallResponseSchema = z.object({
    violatePolicy: z.boolean(),
    content: z.string().default(""),
    violations: z.array(z.string()).optional(),
    reason: z.string().optional(),
    decision_ttl_ms: z.number().int().nonnegative().optional()
})

export type FirewallResponse = z.infer<typeof FirewallResponseSchema>
