#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: verify_phase_3_report.py <staffing-comparison.json>")

path = Path(sys.argv[1])
report = json.loads(path.read_text(encoding="utf-8"))

experiment = report["experiment"]
assert experiment["runCountPerVariant"] == 40, experiment
assert experiment["serverCounts"] == [3, 4, 5], experiment
assert experiment["commonRandomNumbers"] is True, experiment
assert len(report["runs"]) == 120, len(report["runs"])

variants = {item["serverCount"]: item for item in report["variants"]}
assert set(variants) == {3, 4, 5}, variants.keys()

for server_count, variant in variants.items():
    assert variant["runCount"] == 40
    assert variant["arrivalMeanWithinReferenceTolerance"] is True
    assert 0.0 <= variant["successRate"] <= 1.0

    for metric in variant["metrics"].values():
        for value in metric.values():
            if isinstance(value, float):
                assert math.isfinite(value), (server_count, metric)

assert variants[3]["successRate"] < 0.90
assert variants[4]["successRate"] >= 0.90
assert variants[5]["successRate"] >= variants[4]["successRate"]

recommendation = report["recommendation"]
assert recommendation["status"] == "meets_demo_target", recommendation
assert recommendation["serverCount"] == 4, recommendation

output_dir = path.parent
for filename in [
    "staffing-summary.csv",
    "run-level-results.csv",
    "staffing-report.html",
]:
    output = output_dir / filename
    assert output.is_file() and output.stat().st_size > 0, output

print("Phase 3 report verification passed.")
print(
    "Observed success rates:",
    ", ".join(
        f"{server_count} servers={variants[server_count]['successRate']:.1%}"
        for server_count in sorted(variants)
    ),
)
print("Selected demonstration variant: 4 servers")
