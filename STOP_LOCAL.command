#!/bin/zsh
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
docker compose down
echo "QueueForge stopped."
