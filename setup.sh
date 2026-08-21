#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./setup.sh

Installs the OpenSpec CLI globally. Install personal skills with `npx skills`.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi
if [[ $# -gt 0 ]]; then
  usage >&2
  exit 2
fi

require() {
  command -v "$1" >/dev/null || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require npm

npm install --global @fission-ai/openspec
echo "OpenSpec is installed globally. Run 'openspec init' in a project to initialize it."
