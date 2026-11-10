import { existsSync, linkSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs"
import { randomBytes } from "node:crypto"

import { AUTH_FILE, DEEPKEEP_DIR, DEVICE_ID_FILE } from "./paths.js"

export function getDeviceId(): string {
    try {
        if (existsSync(DEVICE_ID_FILE)) return readFileSync(DEVICE_ID_FILE, "utf8").trim() || "unknown-device"
        mkdirSync(DEEPKEEP_DIR, { recursive: true })
        const id = randomBytes(16).toString("hex")
        const temporaryFile = `${DEVICE_ID_FILE}.${id}.tmp`
        writeFileSync(temporaryFile, id, { mode: 0o600, flag: "wx" })
        try {
            try {
                linkSync(temporaryFile, DEVICE_ID_FILE)
            } catch (error) {
                if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error
            }
            return readFileSync(DEVICE_ID_FILE, "utf8").trim() || "unknown-device"
        } finally {
            try { unlinkSync(temporaryFile) } catch { /* best-effort cleanup */ }
        }
    } catch {
        return "unknown-device"
    }
}

export function readBearerFromFile(): string | null {
    try {
        if (!existsSync(AUTH_FILE)) return null
        const data = JSON.parse(readFileSync(AUTH_FILE, "utf8")) as {
            access_token?: string
            expires_at?: number
        }
        if (!data.access_token) return null
        if (typeof data.expires_at === "number" && Date.now() >= data.expires_at) return null
        return data.access_token
    } catch {
        return null
    }
}
