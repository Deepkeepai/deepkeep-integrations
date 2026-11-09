#!/usr/bin/env node
// Copy the freshly built `dist/cli.js` into the Cursor plugin so it ships
// as a self-contained drop-in. Runs after `tsup` (see ``build:plugin``).
//
// Kept as a tiny Node script (instead of a `cp` one-liner) so Windows
// developers can build the plugin without WSL.

import { copyFileSync, existsSync, mkdirSync, chmodSync, statSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, "..")
const src = join(repoRoot, "dist", "cli.js")
const dst = join(repoRoot, "cursor-plugin", "bin", "cli.js")

if (!existsSync(src)) {
    console.error(`[bundle-into-plugin] missing source: ${src}`)
    console.error(`[bundle-into-plugin] run \`npm run build\` first`)
    process.exit(1)
}

mkdirSync(dirname(dst), { recursive: true })
copyFileSync(src, dst)

// Mark executable on POSIX. ``chmod`` is a no-op on Windows, which is fine.
try {
    const mode = statSync(dst).mode | 0o111
    chmodSync(dst, mode)
} catch {
    // Non-fatal — the plugin invokes ``node bin/cli.js``, not the file directly.
}

const sizeKb = (statSync(dst).size / 1024).toFixed(1)
console.log(`[bundle-into-plugin] copied ${src} -> ${dst} (${sizeKb} KB)`)
