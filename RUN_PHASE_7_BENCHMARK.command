#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

docker info >/dev/null
docker compose config >/dev/null

python3 tools/performance/benchmark_phase_7.py
python3 tools/performance/check_phase_7_report.py \
  runtime/phase7/performance-report.json

echo "Phase 7 performance benchmark passed."
