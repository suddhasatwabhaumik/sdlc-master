#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "==> 1. Running Python integrity & sanitization validator..."
python3 scripts/validate_plugin.py

if command -v agy >/dev/null 2>&1; then
  echo "==> 2. Running official Antigravity strict validator on plugin directory..."
  agy plugin validate "${REPO_ROOT}" --strict --json
else
  echo "==> 2. Skipping 'agy plugin validate' (agy CLI not found in PATH)."
fi

VERSION="$(python3 -c 'import json; print(json.load(open("plugin.json"))["version"])')"
PLUGIN_NAME="$(python3 -c 'import json; print(json.load(open("plugin.json"))["name"])')"
OUT_DIR="${REPO_ROOT}/dist"
OUT_ZIP="${OUT_DIR}/${PLUGIN_NAME}-v${VERSION}.zip"

mkdir -p "${OUT_DIR}"
rm -f "${OUT_ZIP}"

echo "==> 3. Building distributable plugin archive: ${OUT_ZIP}"
zip -r "${OUT_ZIP}" \
  plugin.json \
  README.md \
  LICENSE \
  NOTICE \
  assets/ \
  skills/ \
  -x "*.DS_Store" "*__pycache__*"

if command -v agy >/dev/null 2>&1; then
  echo "==> 4. Running official Antigravity strict validator on archive..."
  agy plugin validate "${OUT_ZIP}" --strict --json
fi

echo "==> Done! Packaged plugin ready at: ${OUT_ZIP}"
echo "    Note: extract into a named folder before installing with 'agy plugin install <dir>'."
