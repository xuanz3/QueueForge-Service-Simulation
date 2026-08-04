from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "performance/phase7-budgets.json",
    "tools/quality/verify_repository_quality.py",
    "tools/performance/benchmark_phase_7.py",
    "tools/performance/check_phase_7_report.py",
    "docs/quality/QUALITY_POLICY.md",
    "docs/performance/PERFORMANCE_METHOD.md",
    "docs/decisions/ADR-006-performance-budgets.md",
    "docs/testing/PHASE_7_VERIFICATION.md",
    "RUN_PHASE_7_BENCHMARK.command",
    "VERIFY_PHASE_7.command",
]

for relative in REQUIRED_FILES:
    if not (ROOT / relative).is_file():
        raise SystemExit(f"Missing Phase 7 file: {relative}")

budgets = json.loads(
    (ROOT / "performance/phase7-budgets.json").read_text(encoding="utf-8")
)
if budgets.get("schemaVersion") != "1.0":
    raise SystemExit("Phase 7 budgets schemaVersion must be 1.0")

for section in ["cpp", "analytics", "api", "web", "images"]:
    if not isinstance(budgets.get(section), dict):
        raise SystemExit(f"Phase 7 budget section is missing: {section}")

cmake = (ROOT / "engines/simulation-cpp/CMakeLists.txt").read_text(
    encoding="utf-8"
)
for marker in [
    "QUEUEFORGE_WARNINGS_AS_ERRORS",
    "target_compile_options(${target} PRIVATE -Werror)",
]:
    if marker not in cmake:
        raise SystemExit(f"C++ quality gate is missing: {marker}")


dockerfile = (ROOT / "services/control-plane-java/Dockerfile").read_text(
    encoding="utf-8"
)
for marker in [
    "-DQUEUEFORGE_WARNINGS_AS_ERRORS=ON",
    "ctest --test-dir build --output-on-failure",
]:
    if marker not in dockerfile:
        raise SystemExit(f"Containerized C++ quality stage is missing: {marker}")

phase7_command = (ROOT / "VERIFY_PHASE_7.command").read_text(encoding="utf-8")
for marker in [
    "--target cpp-build",
    "queueforge-cpp-quality:phase7",
    "--file services/control-plane-java/Dockerfile",
]:
    if marker not in phase7_command:
        raise SystemExit(f"Docker C++ verification command is missing: {marker}")

if "\\ncmake \\\\\\n" in phase7_command or "\\nctest " in phase7_command:
    raise SystemExit("Phase 7 still requires host CMake or CTest")

benchmark = (ROOT / "tools/performance/benchmark_phase_7.py").read_text(
    encoding="utf-8"
)
for marker in [
    "benchmark_cpp",
    "benchmark_analytics",
    "benchmark_api",
    "benchmark_web",
    "queueforge-api:latest",
    "queueforge-web:latest",
    "performance-report.json",
    "performance-report.md",
]:
    if marker not in benchmark:
        raise SystemExit(f"Performance benchmark is missing: {marker}")

checker = (ROOT / "tools/performance/check_phase_7_report.py").read_text(
    encoding="utf-8"
)
for marker in [
    "cpp_determinism",
    "api_success_rate",
    "api_end_to_end_p95",
    "web_javascript_size",
    "api_image_size",
]:
    if marker not in checker:
        raise SystemExit(f"Performance report gate is missing: {marker}")

workflow = (ROOT / ".github/workflows/quality.yml").read_text(
    encoding="utf-8"
)
for marker in [
    "quality-performance:",
    "Verify quality and performance",
    "phase7-performance-results",
    "python tools/verify_phase_7.py",
]:
    if marker not in workflow:
        raise SystemExit(f"Phase 7 workflow integration is missing: {marker}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")

phase7_review_markers = [
    "**Phase 7 — Quality and Performance**",
    "8. Quality and performance — in review",
]
final_release_markers = [
    "# QueueForge",
    "## Product screenshots",
    "## Reference measurements",
    "All planned phases are complete in `v1.0.0`.",
    "docs/release/RELEASE_NOTES_v1.0.0.md",
]

phase7_review_state = all(
    marker in readme for marker in phase7_review_markers
)
final_release_state = all(
    marker in readme for marker in final_release_markers
)

if not (phase7_review_state or final_release_state):
    raise SystemExit(
        "README is neither the Phase 7 review state nor the final v1.0.0 state"
    )

print(f"Phase 7 repository verification passed ({len(REQUIRED_FILES)} required files).")
