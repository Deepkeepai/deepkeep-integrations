import { defineConfig } from "tsup"

export default defineConfig({
    entry: { cli: "src/cli.ts" },
    format: ["esm"],
    target: "node20",
    platform: "node",
    splitting: false,
    sourcemap: false,
    clean: true,
    // The plugin ships bin/cli.js with no node_modules alongside it, so every
    // dependency must be inlined. Without this the hook fails at startup with
    // ERR_MODULE_NOT_FOUND on the customer machine.
    noExternal: [/.*/],
    dts: false,
    minify: false,
    // Inlined dependencies are CommonJS (commander, axios) and call `require`
    // at load time, which an ESM bundle has no binding for. Provide one.
    banner: {
        js: [
            "#!/usr/bin/env node",
            'import{createRequire as __dkCreateRequire}from"node:module";',
            "const require=__dkCreateRequire(import.meta.url);"
        ].join("\n")
    },
    outExtension: () => ({ js: ".js" })
})
