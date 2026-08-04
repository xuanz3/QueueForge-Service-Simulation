from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GENERATED_PREFIXES = (
    "runtime/",
    "reports/generated/",
    "demo/generated/",
    "coverage/",
    "test-results/",
    "playwright-report/",
    "apps/web/dist/",
    "apps/web/node_modules/",
    "services/control-plane-java/target/",
    "engines/simulation-cpp/build/",
)

REQUIRED_EXECUTABLES = (
    "VERIFY_PHASE_4.command",
    "VERIFY_PHASE_5.command",
    "VERIFY_PHASE_6.command",
    "VERIFY_PHASE_7.command",
    "RUN_PHASE_7_BENCHMARK.command",
    "tools/faults/slow-simulation.sh",
    "tools/faults/failing-simulation.sh",
    "tools/faults/hanging-simulation.sh",
)

REQUIRED_LOCKS = (
    "apps/web/package-lock.json",
)

REQUIRED_JSON = (
    "contracts/examples/basic-scenario.json",
    "performance/phase7-budgets.json",
)


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line]


tracked = set(git_lines("ls-files"))

generated = sorted(
    path
    for path in tracked
    if any(path.startswith(prefix) for prefix in GENERATED_PREFIXES)
)
if generated:
    raise SystemExit(
        "Generated files must not be tracked:\n" + "\n".join(generated)
    )

for relative in REQUIRED_LOCKS:
    if relative not in tracked or not (ROOT / relative).is_file():
        raise SystemExit(f"Required dependency lock is missing: {relative}")

for relative in REQUIRED_JSON:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"Required JSON file is missing: {relative}")
    with path.open(encoding="utf-8") as handle:
        json.load(handle)

index_modes: dict[str, str] = {}
for line in git_lines("ls-files", "--stage"):
    mode, _, _, path = line.split(maxsplit=3)
    index_modes[path] = mode

for relative in REQUIRED_EXECUTABLES:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"Required executable is missing: {relative}")
    if index_modes.get(relative) != "100755":
        raise SystemExit(f"Git executable bit is missing: {relative}")
    if not os.access(path, os.X_OK):
        raise SystemExit(f"Filesystem executable bit is missing: {relative}")

cmake = (ROOT / "engines/simulation-cpp/CMakeLists.txt").read_text(
    encoding="utf-8"
)
for marker in [
    "QUEUEFORGE_WARNINGS_AS_ERRORS",
    "-Werror",
]:
    if marker not in cmake:
        raise SystemExit(f"C++ quality gate is missing: {marker}")


dockerfile = (ROOT / "services/control-plane-java/Dockerfile").read_text(
    encoding="utf-8"
)
for marker in [
    "-DQUEUEFORGE_WARNINGS_AS_ERRORS=ON",
    "cmake --build build",
    "ctest --test-dir build --output-on-failure",
]:
    if marker not in dockerfile:
        raise SystemExit(f"Containerized C++ quality gate is missing: {marker}")

subprocess.run(
    ["git", "diff", "--check", "HEAD"],
    cwd=ROOT,
    check=True,
)

print("Repository hygiene, locks, JSON and executable modes passed.")
