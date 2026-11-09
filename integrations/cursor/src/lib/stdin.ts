const MAX_STDIN_BYTES = 5 * 1024 * 1024

export async function readStdin(): Promise<string> {
    if (process.stdin.isTTY) return ""

    return await new Promise((resolve, reject) => {
        const chunks: Buffer[] = []
        let total = 0
        let settled = false

        const finish = (err: Error | null, data?: string) => {
            if (settled) return
            settled = true
            if (err) reject(err)
            else resolve(data ?? "")
        }

        process.stdin.on("data", (c: Buffer) => {
            total += c.length
            if (total > MAX_STDIN_BYTES) {
                finish(new Error("stdin payload exceeds 5MB limit"))
                process.stdin.removeAllListeners()
                return
            }
            chunks.push(c)
        })
        process.stdin.on("end", () => finish(null, Buffer.concat(chunks).toString("utf8")))
        process.stdin.on("error", (err) => finish(err))
    })
}

export function parseJson<T = unknown>(raw: string): T | null {
    if (!raw || raw.trim().length === 0) return null
    try {
        return JSON.parse(raw.replace(/^\uFEFF/, "")) as T
    } catch {
        return null
    }
}
