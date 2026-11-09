import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { randomBytes } from "node:crypto"

import { AUTH_FILE, DEEPKEEP_DIR, DEVICE_ID_FILE } from "./paths.js"

export function getDeviceId(): string {
    try {
        if (existsSync(DEVICE_ID_FILE)) {
            const v = readFileSync(DEVICE_ID_FILE, "utf8").trim()
            if (v.length > 0) return v
        }
        mkdirSync(DEEPKEEP_DIR, { recursive: true })
        const id = randomBytes(16).toString("hex")
        writeFileSync(DEVICE_ID_FILE, id, { mode: 0o600 })
        return id
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
