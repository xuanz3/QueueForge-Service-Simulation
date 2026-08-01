#!/bin/zsh
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
CPP="$(docker compose --profile tools run --rm cpp-engine --health)"
PY="$(docker compose --profile tools run --rm python-analytics python -m queueforge_analytics health)"
echo "C++: $CPP"; echo "Python: $PY"
echo "$CPP" | grep -q '"status":"ready"'
echo "$PY" | grep -q '"status":"ready"'
