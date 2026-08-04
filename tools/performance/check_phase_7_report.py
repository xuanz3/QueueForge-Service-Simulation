from __future__ import annotations

import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "runtime/phase7/performance-report.json"
)

if not path.is_file():
    raise SystemExit(f"Performance report is missing: {path}")

report = json.loads(path.read_text(encoding="utf-8"))

if report.get("schemaVersion") != "1.0":
    raise SystemExit("Performance report schemaVersion must be 1.0")

gates = report.get("gates")
if not isinstance(gates, list) or not gates:
    raise SystemExit("Performance report has no gates")

names = {gate.get("name") for gate in gates}
required = {
    "cpp_determinism",
    "cpp_p95",
    "analytics_elapsed",
    "api_success_rate",
    "api_submit_p95",
    "api_end_to_end_p95",
    "web_javascript_size",
    "web_css_size",
    "api_image_size",
    "web_image_size",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("Performance report is missing gates: " + ", ".join(missing))

failed = [gate for gate in gates if gate.get("passed") is not True]
if failed:
    for gate in failed:
        print(
            f"FAILED {gate.get('name')}: "
            f"actual={gate.get('actual')} budget={gate.get('budget')}"
        )
    raise SystemExit("One or more Phase 7 performance budgets failed")

if report.get("passed") is not True:
    raise SystemExit("Performance report did not record an overall pass")

print(f"Phase 7 performance report passed ({len(gates)} gates).")
