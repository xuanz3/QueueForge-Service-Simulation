#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python3 tools/verify_phase_0.py
python3 tools/verify_phase_1.py
python3 tools/verify_cpp_runtime.py
python3 tools/verify_phase_2.py
python3 tools/verify_phase_3.py
python3 tools/verify_phase_4.py
python3 tools/verify_phase_5.py
python3 tools/verify_phase_6.py
python3 tools/verify_phase_7.py
python3 tools/quality/verify_repository_quality.py

docker build \
  --target cpp-build \
  --tag queueforge-cpp-quality:phase7 \
  --file services/control-plane-java/Dockerfile \
  .

PYTHONPATH=analytics/queueforge-python/src \
  python3 -m compileall -q analytics/queueforge-python/src
PYTHONPATH=analytics/queueforge-python/src \
  python3 -m unittest discover \
    -s analytics/queueforge-python/tests \
    -v

docker build \
  --target java-build \
  --tag queueforge-java-quality:phase7 \
  --file services/control-plane-java/Dockerfile \
  .

docker build \
  --target typecheck \
  --tag queueforge-web-typecheck:phase7 \
  apps/web

./RUN_PHASE_7_BENCHMARK.command

echo "Phase 7 verification passed."
