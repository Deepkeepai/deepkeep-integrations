import { homedir } from "node:os"
import { join } from "node:path"

const HOME = homedir()

export const DEEPKEEP_DIR = join(HOME, ".deepkeep")
export const CONFIG_FILE = join(DEEPKEEP_DIR, "config.json")
export const AUTH_FILE = join(DEEPKEEP_DIR, "auth.json")
export const CACHE_FILE = join(DEEPKEEP_DIR, "cache.json")
export const DEVICE_ID_FILE = join(DEEPKEEP_DIR, "device_id")
export const LOG_DIR = join(DEEPKEEP_DIR, "logs")
export const LOG_FILE = join(LOG_DIR, "hook.log")

export const CURSOR_DIR = join(HOME, ".cursor")
export const CURSOR_HOOKS_FILE = join(CURSOR_DIR, "hooks.json")
export const CURSOR_HOOKS_BACKUP = join(CURSOR_DIR, "hooks.json.bak")
