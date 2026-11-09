#!/usr/bin/env bash
# Remove the locally installed plugin.
#
# The plugin registers its own hooks from ``hooks/hooks.json``, so deleting the
# plugin directory is all that is required — nothing was written to
# ``~/.cursor/hooks.json``.
#
# Leaves ``~/.deepkeep/`` alone (config, cache, device id, logs). Remove it
# manually for a full reset.

set -euo pipefail

DEST="${HOME}/.cursor/plugins/local/deepkeep"
HOOKS_FILE="${HOME}/.cursor/hooks.json"

if [[ -e "${DEST}" || -L "${DEST}" ]]; then
    rm -rf "${DEST}"
    echo "✓ removed ${DEST}"
else
    echo "✓ nothing installed at ${DEST}"
fi

# Entries here can only be leftovers from the retired installer, and they would
# keep validating actions after the plugin is gone.
if [[ -f "${HOOKS_FILE}" ]] && grep -q "deepkeep" "${HOOKS_FILE}" 2>/dev/null; then
    echo "[uninstall] WARNING: ${HOOKS_FILE} still contains DeepKeep entries from the retired installer." >&2
    echo "[uninstall] Remove them manually, or those hooks will keep running." >&2
fi

cat <<EOF

✓ DeepKeep plugin uninstalled.

Next: fully quit Cursor (Cmd+Q) and reopen it.

Optional full reset (config, cache, device id, logs):
  rm -rf ~/.deepkeep
EOF
