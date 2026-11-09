#!/usr/bin/env bash
# Install the built plugin into Cursor for local development.
#
# Copies ``cursor-plugin/`` to ``~/.cursor/plugins/local/deepkeep``. Cursor
# skips symlinks whose target resolves outside that folder, so this must be a
# real copy, not a link.
#
# Nothing is written to ``~/.cursor/hooks.json``. The plugin registers its own
# hooks from ``hooks/hooks.json`` when Cursor loads it.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="${REPO_ROOT}/cursor-plugin"
DEST="${HOME}/.cursor/plugins/local/deepkeep"

for required in \
    "${PLUGIN_DIR}/.cursor-plugin/plugin.json" \
    "${PLUGIN_DIR}/hooks/hooks.json" \
    "${PLUGIN_DIR}/bin/cli.js" \
    "${PLUGIN_DIR}/bin/deepkeep-hook"
do
    if [[ ! -f "${required}" ]]; then
        echo "[install] missing ${required} — run 'npm run build:plugin' first" >&2
        exit 1
    fi
done

# A stale DeepKeep entry in the user hooks file would run alongside the
# plugin's own hooks and double-validate every action.
if [[ -f "${HOME}/.cursor/hooks.json" ]] && grep -q "deepkeep" "${HOME}/.cursor/hooks.json" 2>/dev/null; then
    echo "[install] WARNING: ~/.cursor/hooks.json still contains DeepKeep entries from the retired installer." >&2
    echo "[install] Remove them manually - the plugin registers its own hooks." >&2
fi

rm -rf "${DEST}"
mkdir -p "$(dirname "${DEST}")"
cp -R "${PLUGIN_DIR}" "${DEST}"
chmod +x "${DEST}/bin/deepkeep-hook"

cat <<EOF

✓ DeepKeep plugin installed.

  Location : ${DEST}
  Hooks    : registered by the plugin itself (~/.cursor/hooks.json untouched)

Next: fully quit Cursor (Cmd+Q) and reopen it, then verify with
  DEEPKEEP_DEBUG=1 tail -f ~/.deepkeep/logs/hook.log
EOF
