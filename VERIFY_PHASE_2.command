#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python3 tools/verify_phase_0.py
python3 tools/verify_phase_1.py
python3 tools/verify_cpp_runtime.py
python3 tools/verify_phase_2.py

docker info >/dev/null
docker compose config >/dev/null
docker compose --profile tools build cpp-engine

./RUN_ENGINE_DEMO.command

echo "Phase 2 verification passed."
