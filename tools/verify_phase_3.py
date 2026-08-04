#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "analytics/queueforge-python/src/queueforge_analytics/engine.py",
    "analytics/queueforge-python/src/queueforge_analytics/statistics.py",
    "analytics/queueforge-python/src/queueforge_analytics/reference.py",
    "analytics/queueforge-python/src/queueforge_analytics/experiment.py",
    "analytics/queueforge-python/src/queueforge_analytics/reporting.py",
    "analytics/queueforge-python/tests/test_statistics.py",
    "analytics/queueforge-python/tests/test_reference.py",
    "analytics/queueforge-python/tests/test_experiment.py",
    "analytics/queueforge-python/tests/test_reporting.py",
    "contracts/schemas/analytics-report.schema.json",
    "RUN_ANALYTICS_DEMO.command",
    "VERIFY_PHASE_3.command",
    "tools/verify_phase_3_report.py",
    "docs/analytics/EXPERIMENT_METHOD.md",
    "docs/decisions/ADR-004-common-random-numbers.md",
    "docs/testing/PHASE_3_VERIFICATION.md",
]

missing = [item for item in REQUIRED_FILES if not (ROOT / item).is_file()]
if missing:
    raise SystemExit(
        "Missing Phase 3 files:\n" + "\n".join(f"- {item}" for item in missing)
    )

for relative in [
    "contracts/schemas/analytics-report.schema.json",
    "analytics/queueforge-python/pyproject.toml",
]:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"Phase 3 file is empty: {relative}")

with (ROOT / "contracts/schemas/analytics-report.schema.json").open(
    encoding="utf-8"
) as stream:
    json.load(stream)

for relative in ["RUN_ANALYTICS_DEMO.command", "VERIFY_PHASE_3.command"]:
    if not os.access(ROOT / relative, os.X_OK):
        raise SystemExit(f"Phase 3 command is not executable: {relative}")

compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
required_compose = [
    "python-analytics:",
    "context: .",
    "dockerfile: analytics/queueforge-python/Dockerfile",
]
for item in required_compose:
    if item not in compose:
        raise SystemExit(f"compose.yaml is missing Phase 3 configuration: {item}")

demo = (ROOT / "RUN_ANALYTICS_DEMO.command").read_text(encoding="utf-8")
for item in [
    "--server-counts 3,4,5",
    "--runs 40",
    "--seed-start 20260801",
    "find runtime/phase3 -maxdepth 1 -type f -delete",
]:
    if item not in demo:
        raise SystemExit(f"Analytics demo is missing fixed evidence setting: {item}")

print(f"Phase 3 repository verification passed ({len(REQUIRED_FILES)} required files).")
