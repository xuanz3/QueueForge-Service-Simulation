#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python3 tools/verify_phase_0.py
python3 tools/verify_phase_1.py
python3 tools/verify_cpp_runtime.py
python3 tools/verify_phase_2.py
python3 tools/verify_phase_3.py

docker info >/dev/null
docker compose config >/dev/null

./RUN_ANALYTICS_DEMO.command

echo "Phase 3 verification passed."
