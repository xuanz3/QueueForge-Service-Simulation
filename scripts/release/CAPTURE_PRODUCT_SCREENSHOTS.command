#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SCREENSHOT_PORT=15177
PLAYWRIGHT_IMAGE="mcr.microsoft.com/playwright:v1.55.0-noble"

restore_normal_stack() {
  printf "\nRestoring the normal QueueForge stack on port 15176...\n"
  unset QUEUEFORGE_WEB_PORT
  docker compose -f compose.yaml up -d --build --force-recreate \
    postgres api web
}

trap restore_normal_stack EXIT

docker info >/dev/null
docker compose config >/dev/null

./VERIFY_PHASE_6.command
./RUN_PHASE_7_BENCHMARK.command

export QUEUEFORGE_WEB_PORT="$SCREENSHOT_PORT"
docker compose \
  -f compose.yaml \
  -f compose.screenshots.yaml \
  up -d --build --force-recreate postgres api web

for attempt in {1..120}; do
  if curl -fsS http://localhost:18086/actuator/health/readiness >/dev/null \
      && curl -fsS "http://localhost:${SCREENSHOT_PORT}" >/dev/null; then
    break
  fi
  if [ "$attempt" -eq 120 ]; then
    echo "Screenshot stack did not become ready." >&2
    exit 1
  fi
  sleep 1
done

docker run --rm \
  --ipc=host \
  --user "$(id -u):$(id -g)" \
  --add-host=host.docker.internal:host-gateway \
  -e HOME=/tmp/queueforge-home \
  -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
  -e QUEUEFORGE_SCREENSHOT_URL="http://host.docker.internal:${SCREENSHOT_PORT}" \
  -v "$ROOT:/work" \
  -w /work \
  "$PLAYWRIGHT_IMAGE" \
  bash -lc '
    mkdir -p "$HOME" /tmp/queueforge-pw
    npm install --prefix /tmp/queueforge-pw --no-save playwright@1.55.0 >/dev/null
    NODE_PATH=/tmp/queueforge-pw/node_modules \
      node tools/screenshots/capture_product_screenshots.cjs
  '

python3 tools/release/render_release_docs.py
python3 tools/verify_release_screenshots.py

trap - EXIT
restore_normal_stack

echo "QueueForge screenshot capture passed."
