#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

./VERIFY_PHASE_7.command
python3 tools/verify_phase_8.py

docker compose -f compose.yaml up -d --build postgres api web

for attempt in {1..120}; do
  if curl -fsS http://localhost:18086/actuator/health/readiness >/dev/null \
      && curl -fsS http://localhost:15176 >/dev/null; then
    docker compose ps
    echo "Phase 8 release verification passed."
    exit 0
  fi
  sleep 1
done

echo "The final normal product stack did not become ready." >&2
exit 1
