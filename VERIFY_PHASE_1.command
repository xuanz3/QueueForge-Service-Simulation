#!/bin/zsh
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
[ -f .env ] || cp .env.example .env
python3 tools/verify_phase_1.py
docker info >/dev/null
docker compose config >/dev/null
docker compose --profile tools build
docker compose up -d postgres api web
for i in {1..60}; do curl -fsS http://localhost:18086/api/system/status > /tmp/queueforge-status.json && break; [ "$i" -eq 60 ] && { docker compose logs --no-color; exit 1; }; sleep 2; done
python3 - <<'CHECK'
import json
p=json.load(open('/tmp/queueforge-status.json'))
assert p['status']=='ready' and p['database']=='ready', p
print('Java API and PostgreSQL integration passed.')
CHECK
curl -fsS http://localhost:15176 >/dev/null
./RUN_COMPONENT_CHECKS.command
echo "Phase 1 verification passed."
