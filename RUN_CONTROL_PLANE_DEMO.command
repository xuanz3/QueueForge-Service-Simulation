#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p runtime/phase4
find runtime/phase4 -maxdepth 1 -type f -delete

python3 - <<'PY_REQUESTS'
import json
from pathlib import Path

root = Path("runtime/phase4")
scenario = json.loads(Path("contracts/examples/basic-scenario.json").read_text())

(root / "simulation-request.json").write_text(json.dumps({
    "type": "SIMULATION",
    "scenario": scenario,
}, indent=2))

(root / "analytics-request.json").write_text(json.dumps({
    "type": "ANALYTICS",
    "scenario": scenario,
    "serverCounts": [3, 4, 5],
    "runs": 5,
    "seedStart": 20260801,
    "targetP95Wait": 10,
    "targetMaxQueue": 20,
    "targetMaxUtilisation": 0.85,
    "requiredSuccessRate": 0.90,
}, indent=2))

(root / "cancellation-request.json").write_text(json.dumps({
    "type": "ANALYTICS",
    "scenario": scenario,
    "serverCounts": [2, 3, 4, 5, 6],
    "runs": 200,
    "seedStart": 20260801,
}, indent=2))

invalid = json.loads(json.dumps(scenario))
invalid["service"]["minimumMinutes"] = 20
invalid["service"]["modeMinutes"] = 8
(root / "invalid-request.json").write_text(json.dumps({
    "type": "SIMULATION",
    "scenario": invalid,
}, indent=2))
PY_REQUESTS

docker compose up -d --build postgres api

for attempt in {1..120}; do
  if curl -fsS http://localhost:18086/api/system/status \
      > runtime/phase4/system-status.json; then
    break
  fi
  if [ "$attempt" -eq 120 ]; then
    docker compose logs --no-color postgres api
    exit 1
  fi
  sleep 2
done

submit_run() {
  local request_file="$1"
  local response_file="$2"
  curl -fsS \
    -X POST \
    -H 'Content-Type: application/json' \
    --data-binary "@$request_file" \
    http://localhost:18086/api/runs > "$response_file"
  python3 - "$response_file" <<'PY_ID'
import json, sys
payload = json.load(open(sys.argv[1]))
print(payload["id"])
PY_ID
}

wait_for_terminal() {
  local run_id="$1"
  local response_file="$2"
  local run_status=""
  for attempt in {1..180}; do
    curl -fsS "http://localhost:18086/api/runs/$run_id" > "$response_file"
    run_status="$(python3 - "$response_file" <<'PY_STATUS'
import json, sys
print(json.load(open(sys.argv[1]))["status"])
PY_STATUS
)"
    case "$run_status" in
      SUCCEEDED|FAILED|CANCELLED)
        echo "$run_status"
        return 0
        ;;
    esac
    sleep 1
  done
  echo "Run did not reach a terminal state: $run_id" >&2
  return 1
}

SIMULATION_ID="$(submit_run runtime/phase4/simulation-request.json runtime/phase4/simulation-created.json)"
SIMULATION_STATUS="$(wait_for_terminal "$SIMULATION_ID" runtime/phase4/simulation-status.json)"
[ "$SIMULATION_STATUS" = "SUCCEEDED" ] || {
  cat runtime/phase4/simulation-status.json
  docker compose logs --no-color api
  exit 1
}
curl -fsS "http://localhost:18086/api/runs/$SIMULATION_ID/result" \
  > runtime/phase4/simulation-result.json

ANALYTICS_ID="$(submit_run runtime/phase4/analytics-request.json runtime/phase4/analytics-created.json)"
ANALYTICS_STATUS="$(wait_for_terminal "$ANALYTICS_ID" runtime/phase4/analytics-status.json)"
[ "$ANALYTICS_STATUS" = "SUCCEEDED" ] || {
  cat runtime/phase4/analytics-status.json
  docker compose logs --no-color api
  exit 1
}
curl -fsS "http://localhost:18086/api/runs/$ANALYTICS_ID/result" \
  > runtime/phase4/analytics-result.json

INVALID_STATUS="$(curl -sS \
  -o runtime/phase4/invalid-response.json \
  -w '%{http_code}' \
  -X POST \
  -H 'Content-Type: application/json' \
  --data-binary @runtime/phase4/invalid-request.json \
  http://localhost:18086/api/runs)"
[ "$INVALID_STATUS" = "400" ] || {
  echo "Expected invalid request HTTP 400, received $INVALID_STATUS" >&2
  cat runtime/phase4/invalid-response.json >&2
  exit 1
}

CANCEL_ID="$(submit_run runtime/phase4/cancellation-request.json runtime/phase4/cancel-created.json)"
curl -fsS -X POST "http://localhost:18086/api/runs/$CANCEL_ID/cancel" \
  > runtime/phase4/cancel-response.json
CANCEL_STATUS="$(wait_for_terminal "$CANCEL_ID" runtime/phase4/cancel-status.json)"
[ "$CANCEL_STATUS" = "CANCELLED" ] || {
  echo "Expected cancellation status, received $CANCEL_STATUS" >&2
  cat runtime/phase4/cancel-status.json >&2
  exit 1
}

python3 - <<'PY_VERIFY'
import json
from pathlib import Path

root = Path("runtime/phase4")
status = json.loads((root / "system-status.json").read_text())
assert status["status"] == "ready", status
assert status["database"] == "ready", status
assert all(value == "ready" for value in status["workers"].values()), status

simulation = json.loads((root / "simulation-result.json").read_text())
assert simulation["invariants"]["accountingBalanced"] is True
assert simulation["invariants"]["chronologyValid"] is True
assert simulation["invariants"]["utilisationWithinRange"] is True

analytics = json.loads((root / "analytics-result.json").read_text())
assert analytics["experiment"]["runCountPerVariant"] == 5
assert analytics["experiment"]["serverCounts"] == [3, 4, 5]
assert len(analytics["runs"]) == 15
assert len(analytics["variants"]) == 3

invalid = json.loads((root / "invalid-response.json").read_text())
assert invalid["status"] == 400, invalid

cancelled = json.loads((root / "cancel-status.json").read_text())
assert cancelled["status"] == "CANCELLED", cancelled

print("Simulation lifecycle: passed")
print("Analytics lifecycle: passed")
print("Invalid request problem detail: passed")
print("Cancellation lifecycle: passed")
PY_VERIFY

RUN_COUNT="$(docker compose exec -T postgres \
  psql -U queueforge -d queueforge -Atc \
  "SELECT COUNT(*) FROM queueforge_run;")"
[ "$RUN_COUNT" -ge 3 ] || {
  echo "Expected at least three persisted runs, received $RUN_COUNT" >&2
  exit 1
}

docker compose restart api
for attempt in {1..120}; do
  if curl -fsS "http://localhost:18086/api/runs/$SIMULATION_ID" \
      > runtime/phase4/simulation-after-restart.json; then
    break
  fi
  if [ "$attempt" -eq 120 ]; then
    docker compose logs --no-color api
    exit 1
  fi
  sleep 2
done

python3 - <<'PY_RESTART'
import json
from pathlib import Path
payload = json.loads(Path("runtime/phase4/simulation-after-restart.json").read_text())
assert payload["status"] == "SUCCEEDED", payload
print("PostgreSQL persistence across API restart: passed")
PY_RESTART

echo "QueueForge control-plane demo passed."
