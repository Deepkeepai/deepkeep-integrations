import { afterEach, describe, expect, it, vi } from "vitest"

import { runDoctor } from "../src/commands/doctor.js"
import * as auth from "../src/lib/auth.js"
import * as config from "../src/lib/config.js"
import * as firewall from "../src/lib/firewall-client.js"

vi.mock("node:fs", async (importOriginal) => {
    const actual = await importOriginal<typeof import("node:fs")>()
    return { ...actual, existsSync: vi.fn(() => false) }
})

describe("doctor authentication", () => {
    afterEach(() => vi.restoreAllMocks())

    it.each([
        ["API key", "key", null, null, 0],
        ["configured bearer", null, "test-secret-credential", null, 0],
        ["stored bearer", null, null, "test-secret-credential", 0],
        ["missing credentials", null, null, null, 1]
    ])("handles %s", async (_name, apiKey, bearerToken, storedToken, exitCode) => {
        vi.spyOn(auth, "getDeviceId").mockReturnValue("test-device")
        vi.spyOn(auth, "readBearerFromFile").mockReturnValue(storedToken)
        vi.spyOn(config, "loadConfig").mockReturnValue({
            firewallUrl: "https://example.com", apiKey, bearerToken, failMode: "block",
            timeoutMs: 1000, cacheTtlMs: 0, deviceId: "test-device", hostname: "host", os: "test", cliVersion: "test"
        })
        vi.spyOn(firewall, "validate").mockResolvedValue({ violatePolicy: false, content: "" })
        const output = vi.spyOn(process.stdout, "write").mockImplementation(() => true)
        const exit = vi.spyOn(process, "exit").mockImplementation(() => { throw new Error("exit") })
        await expect(runDoctor()).rejects.toThrow("exit")
        expect(exit).toHaveBeenCalledWith(exitCode)
        expect(output.mock.calls.map(([line]) => String(line)).join("")).not.toContain("test-secret-credential")
    })
})
