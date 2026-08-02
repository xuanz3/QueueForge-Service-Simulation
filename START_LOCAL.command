#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"
[ -f .env ] || cp .env.example .env
docker info >/dev/null
docker compose up -d --build postgres api web
for i in {1..60}; do curl -fsS http://localhost:18086/api/system/status >/dev/null && break; [ "$i" -eq 60 ] && { docker compose logs --no-color; exit 1; }; sleep 2; done
for i in {1..30}; do curl -fsS http://localhost:15176 >/dev/null && break; [ "$i" -eq 30 ] && { docker compose logs --no-color web; exit 1; }; sleep 2; done
echo "QueueForge ready: http://localhost:15176"
open http://localhost:15176
