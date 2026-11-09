export function validAttachments(value: unknown): boolean {
    return value == null || (Array.isArray(value) && value.every(
        (attachment: unknown) => attachment !== null
            && typeof attachment === "object"
            && typeof (attachment as Record<string, unknown>).file_path === "string"
    ))
}
