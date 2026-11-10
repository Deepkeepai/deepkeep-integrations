import { createHash } from "node:crypto"

import { validAttachments } from "../../lib/attachments.js"
import type { BeforeReadFileInput, PermissionOutput } from "../../types/cursor-hooks.js"

import { helpers, runHook } from "./runner.js"

function summarise(content: string): { content: string; truncated: boolean; sha256: string; size: number } {
    const sha = createHash("sha256").update(content).digest("hex")
    return { content, truncated: false, sha256: sha, size: content.length }
}

export async function runFileReadHook(): Promise<void> {
    await runHook<BeforeReadFileInput, PermissionOutput>({
        action: "before-file-read",
        parseInput: (raw) => {
            if (!raw || typeof raw !== "object") return null
            const r = raw as Record<string, unknown>
            if (typeof r.file_path !== "string" || typeof r.content !== "string" || !validAttachments(r.attachments)) return null
            return {
                file_path: r.file_path,
                content: r.content,
                attachments: Array.isArray(r.attachments)
                    ? (r.attachments as BeforeReadFileInput["attachments"])
                    : []
            }
        },
        buildPayload: (i) => {
            const s = summarise(i.content)
            return {
                file_path: i.file_path,
                content: s.content,
                content_truncated: s.truncated,
                content_size: s.size,
                content_sha256: s.sha256,
                attachment_paths: (i.attachments ?? []).map((a) => a.file_path)
            }
        },
        onFailOpen: () => helpers.failOpenPermission(),
        onFailClosed: () => helpers.failClosedPermission(),
        mapResponse: (res) => helpers.toPermissionOutput(res)
    })
}
