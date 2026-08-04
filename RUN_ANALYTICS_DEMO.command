#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p runtime/phase3
find runtime/phase3 -maxdepth 1 -type f -delete

docker compose --profile tools build python-analytics

docker compose --profile tools run --rm -T --no-deps \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$ROOT/contracts/examples:/inputs:ro" \
  -v "$ROOT/runtime/phase3:/reports" \
  python-analytics \
  python -m queueforge_analytics experiment \
  --scenario /inputs/basic-scenario.json \
  --output-dir /reports \
  --server-counts 3,4,5 \
  --runs 40 \
  --seed-start 20260801 \
  --target-p95-wait 10 \
  --target-max-queue 20 \
  --target-max-utilisation 0.85 \
  --required-success-rate 0.90

python3 tools/verify_phase_3_report.py \
  runtime/phase3/staffing-comparison.json

echo "QueueForge analytics demo passed."
