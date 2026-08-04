#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "docs/product/PROJECT_BRIEF.md",
    "docs/product/SCOPE.md",
    "docs/product/USER_STORIES.md",
    "docs/product/METRICS_AND_ASSUMPTIONS.md",
    "docs/architecture/SYSTEM_CONTEXT.md",
    "docs/decisions/ADR-001-polyglot-architecture.md",
    "docs/decisions/ADR-002-cli-json-integration.md",
    "docs/testing/DEFINITION_OF_DONE.md",
    "docs/project/SCREENSHOT_PLAN.md",
    "docs/operations/ZERO_COST_POLICY.md",
    "contracts/schemas/simulation-input.schema.json",
    "contracts/examples/basic-scenario.json",
]

missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
if missing:
    print("Missing required Phase 0 files:")
    for item in missing:
        print(f"  - {item}")
    sys.exit(1)

for relative in [
    "contracts/schemas/simulation-input.schema.json",
    "contracts/examples/basic-scenario.json",
]:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        json.load(handle)

print("Phase 0 verification passed.")
print(f"Verified {len(REQUIRED)} required files and valid JSON documents.")
