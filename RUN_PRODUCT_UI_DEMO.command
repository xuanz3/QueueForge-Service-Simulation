#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p runtime/phase5
find runtime/phase5 -maxdepth 1 -type f -delete

docker compose up -d --build postgres api web
python3 tools/verify_phase_5_runtime.py

echo "QueueForge product-interface demo passed."
