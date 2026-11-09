import axios, { AxiosError } from "axios"

import { readBearerFromFile } from "./auth.js"
import type { RuntimeConfig } from "./config.js"
import { log } from "./logger.js"
import { FirewallResponseSchema, type FirewallRequest, type FirewallResponse } from "../types/firewall.js"

export class FirewallError extends Error {
    constructor(
        message: string,
        public readonly cause?: unknown
    ) {
        super(message)
        this.name = "FirewallError"
    }
}

export class RedactionUnsupportedError extends FirewallError {}

const HTTP_UNAUTHORIZED = 401
const HTTP_FORBIDDEN = 403
const HTTP_RATE_LIMITED = 429

function buildHeaders(cfg: RuntimeConfig): Record<string, string> {
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        "User-Agent": `deepkeep-hook/${cfg.cliVersion}`
    }

    if (cfg.apiKey) headers["x-api-key"] = cfg.apiKey

    const bearer = cfg.bearerToken ?? readBearerFromFile()
    if (bearer) headers["Authorization"] = `Bearer ${bearer}`

    return headers
}

export async function validate(cfg: RuntimeConfig, req: FirewallRequest): Promise<FirewallResponse> {
    if (!cfg.firewallUrl) {
        throw new FirewallError("DEEPKEEP_FIREWALL_URL not configured")
    }

    try {
        const url = new URL(cfg.firewallUrl)
        if (url.protocol !== "https:" || url.username || url.password) throw new Error()
    } catch {
        throw new FirewallError("Policy endpoint must be a valid HTTPS URL without embedded credentials")
    }

    try {
        const res = await axios.post(cfg.firewallUrl, req, {
            timeout: cfg.timeoutMs,
            headers: buildHeaders(cfg),
            maxRedirects: 0,
            validateStatus: (s) => s >= 200 && s < 300
        })
        if (res.data && typeof res.data === "object" && typeof res.data.redacted_text === "string") {
            throw new RedactionUnsupportedError("Redacted responses are not supported")
        }
        return FirewallResponseSchema.parse(res.data)
    } catch (err) {
        if (err instanceof RedactionUnsupportedError) throw err
        const status =
            err instanceof AxiosError ? (err.response?.status ?? null) : null
        const failure = status === HTTP_UNAUTHORIZED || status === HTTP_FORBIDDEN
            ? "authentication rejected"
            : status === HTTP_RATE_LIMITED
                ? "rate limited"
                : status !== null
                    ? "HTTP error"
                    : err instanceof AxiosError
                        ? "network error"
                        : "invalid response"
        log("warn", "firewall.validate failed", {
            failure,
            status,
            err_code: err instanceof AxiosError ? err.code : undefined,
            action: req.action
        })
        throw new FirewallError(`Firewall validation failed: ${failure}${status === null ? "" : ` (${status})`}`, err)
    }
}
