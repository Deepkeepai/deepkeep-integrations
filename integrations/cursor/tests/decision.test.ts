import { describe, expect, it } from "vitest"

import {
    explain,
    failClosedPermission,
    failClosedPrompt,
    failOpenPermission,
    failOpenPrompt,
    toPermissionOutput,
    toPromptOutput
} from "../src/lib/decision.js"

describe("decision", () => {
    it("allows when policy is not violated", () => {
        expect(toPromptOutput({ violatePolicy: false, content: "" })).toEqual({ continue: true })
        expect(toPermissionOutput({ violatePolicy: false, content: "" })).toEqual({ permission: "allow" })
    })

    it("denies with reason when policy is violated", () => {
        const res = { violatePolicy: true, content: "", reason: "secret detected" }
        expect(toPromptOutput(res)).toEqual({ continue: false, user_message: "secret detected" })
        const perm = toPermissionOutput(res)
        expect(perm.permission).toBe("deny")
        expect(perm.user_message).toBe("secret detected")
        expect(perm.agent_message).toBe("secret detected")
    })

    it("falls back to violations list when no reason", () => {
        const msg = explain({ violatePolicy: true, content: "", violations: ["pii", "injection"] })
        expect(msg).toBe("Policy violations: pii, injection")
    })

    it("fail-open returns allow", () => {
        expect(failOpenPrompt()).toEqual({ continue: true })
        expect(failOpenPermission()).toEqual({ permission: "allow" })
    })

    it("fail-closed returns deny with explanation", () => {
        expect(failClosedPrompt().continue).toBe(false)
        expect(failClosedPermission().permission).toBe("deny")
    })
})
