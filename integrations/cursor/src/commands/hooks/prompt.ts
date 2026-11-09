import type { BeforeSubmitPromptInput } from "../../types/cursor-hooks.js"
import { validAttachments } from "../../lib/attachments.js"

import { helpers, runHook } from "./runner.js"

export async function runPromptHook(): Promise<void> {
    await runHook<BeforeSubmitPromptInput, { continue: boolean; user_message?: string }>({
        action: "before-prompt",
        parseInput: (raw) => {
            if (!raw || typeof raw !== "object") return null
            const r = raw as Record<string, unknown>
            if (typeof r.prompt !== "string") return null
            if (!validAttachments(r.attachments)) return null
            return {
                prompt: r.prompt,
                attachments: Array.isArray(r.attachments)
                    ? (r.attachments as BeforeSubmitPromptInput["attachments"])
                    : []
            }
        },
        buildPayload: (i) => ({
            prompt: i.prompt,
            attachment_paths: (i.attachments ?? []).map((a) => a.file_path)
        }),
        onFailOpen: () => helpers.failOpenPrompt(),
        onFailClosed: () => helpers.failClosedPrompt(),
        mapResponse: (res) => helpers.toPromptOutput(res)
    })
}
