#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p runtime/phase2
find runtime/phase2 -maxdepth 1 -type f -name '*.json' -delete

run_engine() {
  local input_path="$1"
  local output_path="$2"

  docker compose --profile tools run --rm -T --no-deps \
    -v "$ROOT/contracts/examples:/inputs:ro" \
    cpp-engine \
    --input "/inputs/$input_path" \
    --output - \
    --pretty > "$output_path"
}

run_engine "basic-scenario.json" "runtime/phase2/basic-result-1.json"
run_engine "basic-scenario.json" "runtime/phase2/basic-result-2.json"
cmp runtime/phase2/basic-result-1.json runtime/phase2/basic-result-2.json

run_engine "overloaded-scenario.json" "runtime/phase2/overloaded-result.json"

docker compose --profile tools run --rm -T --no-deps \
  -v "$ROOT/contracts/examples:/inputs:ro" \
  cpp-engine \
  --input /inputs/basic-scenario.json \
  --output - \
  --validate-only > runtime/phase2/validation-result.json

set +e
docker compose --profile tools run --rm -T --no-deps \
  -v "$ROOT/engines/simulation-cpp/tests/fixtures:/fixtures:ro" \
  cpp-engine \
  --input /fixtures/invalid-service-order.json \
  --output - > runtime/phase2/invalid-output.json 2> runtime/phase2/invalid-error.txt
INVALID_STATUS=$?
set -e

if [ "$INVALID_STATUS" -ne 65 ]; then
  echo "Expected invalid input exit code 65, received $INVALID_STATUS." >&2
  cat runtime/phase2/invalid-error.txt >&2
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path

root = Path("runtime/phase2")
basic = json.loads((root / "basic-result-1.json").read_text())
overloaded = json.loads((root / "overloaded-result.json").read_text())
validation = json.loads((root / "validation-result.json").read_text())

for name, result in [("basic", basic), ("overloaded", overloaded)]:
    metrics = result["metrics"]
    invariants = result["invariants"]

    assert metrics["arrived"] == (
        metrics["completed"]
        + metrics["waitingAtEnd"]
        + metrics["inServiceAtEnd"]
    ), (name, metrics)
    assert invariants["accountingBalanced"] is True
    assert invariants["chronologyValid"] is True
    assert invariants["utilisationWithinRange"] is True
    assert 0 <= metrics["overallUtilisation"] <= 1
    assert len(result["servers"]) > 0
    assert len(result["events"]) > 0

assert overloaded["metrics"]["maximumQueueLength"] > 0
assert validation == {"schemaVersion": "1.0", "status": "valid"}

print("Deterministic repeat: passed")
print(
    "Basic scenario:",
    f"arrived={basic['metrics']['arrived']},",
    f"completed={basic['metrics']['completed']},",
    f"p95_wait={basic['metrics']['p95WaitMinutes']:.3f} minutes,",
    f"max_queue={basic['metrics']['maximumQueueLength']}",
)
print(
    "Overloaded scenario:",
    f"arrived={overloaded['metrics']['arrived']},",
    f"completed={overloaded['metrics']['completed']},",
    f"waiting_at_end={overloaded['metrics']['waitingAtEnd']},",
    f"max_queue={overloaded['metrics']['maximumQueueLength']}",
)
print("Invalid contract rejection: passed with exit code 65")
PY

echo "QueueForge engine demo passed."
