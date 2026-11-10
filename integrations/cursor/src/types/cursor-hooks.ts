export interface CursorAttachment {
    type: "file" | "rule"
    file_path: string
}

export interface BeforeSubmitPromptInput {
    prompt: string
    attachments?: CursorAttachment[]
}

export interface BeforeShellExecutionInput {
    command: string
    cwd?: string
    sandbox?: boolean
}

export interface BeforeReadFileInput {
    file_path: string
    content: string
    attachments?: CursorAttachment[]
}

export interface BeforeMCPExecutionInput {
    tool_name: string
    tool_input: unknown
    url?: string
    command?: string
}

export interface PromptOutput {
    continue: boolean
    user_message?: string
}

export interface PermissionOutput {
    permission: "allow" | "deny" | "ask"
    user_message?: string
    agent_message?: string
    updated_input?: Record<string, unknown>
}

export type CursorHookEvent =
    | "beforeSubmitPrompt"
    | "beforeShellExecution"
    | "beforeReadFile"
    | "beforeMCPExecution"
