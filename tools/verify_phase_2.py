#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "engines/simulation-cpp/include/queueforge/json.hpp",
    "engines/simulation-cpp/include/queueforge/json_io.hpp",
    "engines/simulation-cpp/include/queueforge/model.hpp",
    "engines/simulation-cpp/include/queueforge/random.hpp",
    "engines/simulation-cpp/include/queueforge/simulator.hpp",
    "engines/simulation-cpp/include/queueforge/waiting_queue.hpp",
    "engines/simulation-cpp/src/json.cpp",
    "engines/simulation-cpp/src/json_io.cpp",
    "engines/simulation-cpp/src/model.cpp",
    "engines/simulation-cpp/src/random.cpp",
    "engines/simulation-cpp/src/simulator.cpp",
    "engines/simulation-cpp/src/waiting_queue.cpp",
    "engines/simulation-cpp/tests/json_test.cpp",
    "engines/simulation-cpp/tests/json_io_test.cpp",
    "engines/simulation-cpp/tests/simulator_test.cpp",
    "engines/simulation-cpp/tests/waiting_queue_test.cpp",
    "engines/simulation-cpp/tests/fixtures/invalid-service-order.json",
    "contracts/schemas/simulation-result.schema.json",
    "contracts/examples/overloaded-scenario.json",
    "RUN_ENGINE_DEMO.command",
    "VERIFY_PHASE_2.command",
    "docs/architecture/ENGINE_DESIGN.md",
    "docs/decisions/ADR-003-deterministic-randomness.md",
    "docs/testing/PHASE_2_VERIFICATION.md",
]

missing = [item for item in REQUIRED_FILES if not (ROOT / item).is_file()]
if missing:
    raise SystemExit("Missing Phase 2 files:\n" + "\n".join(f"- {item}" for item in missing))

for relative in [
    "contracts/schemas/simulation-input.schema.json",
    "contracts/schemas/simulation-result.schema.json",
    "contracts/examples/basic-scenario.json",
    "contracts/examples/overloaded-scenario.json",
]:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        json.load(handle)


for relative in [
    "RUN_ENGINE_DEMO.command",
    "VERIFY_PHASE_2.command",
]:
    command_path = ROOT / relative
    if not os.access(command_path, os.X_OK):
        raise SystemExit(f"Phase 2 command is not executable: {relative}")


demo_script = (ROOT / "RUN_ENGINE_DEMO.command").read_text(encoding="utf-8")
unsafe_cleanup = "rm -f runtime/phase2/*.json"
safe_cleanup = "find runtime/phase2 -maxdepth 1 -type f -name '*.json' -delete"

if unsafe_cleanup in demo_script:
    raise SystemExit("Phase 2 demo uses a zsh-unsafe unmatched wildcard cleanup.")

if safe_cleanup not in demo_script:
    raise SystemExit("Phase 2 demo is missing the safe JSON cleanup command.")

cmake = (ROOT / "engines/simulation-cpp/CMakeLists.txt").read_text(encoding="utf-8")
for required in [
    "QUEUEFORGE_ENABLE_SANITIZERS",
    "queueforge-json-tests",
    "queueforge-json-io-tests",
    "queueforge-simulator-tests",
    "queueforge-waiting-queue-tests",
]:
    if required not in cmake:
        raise SystemExit(f"CMakeLists.txt is missing Phase 2 requirement: {required}")

main = (ROOT / "engines/simulation-cpp/src/main.cpp").read_text(encoding="utf-8")
for flag in ["--input", "--output", "--validate-only", "--pretty"]:
    if flag not in main:
        raise SystemExit(f"CLI implementation is missing flag: {flag}")

print(f"Phase 2 repository verification passed ({len(REQUIRED_FILES)} required files).")
