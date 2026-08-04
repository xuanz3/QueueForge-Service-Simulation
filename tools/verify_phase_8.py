from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "compose.screenshots.yaml",
    "scripts/release/CAPTURE_PRODUCT_SCREENSHOTS.command",
    "VERIFY_PHASE_8.command",
    "tools/screenshots/capture_product_screenshots.cjs",
    "tools/release/render_release_docs.py",
    "tools/verify_phase_8.py",
    "tools/verify_release_screenshots.py",
    "tools/quality/verify_public_metadata.py",
    "docs/decisions/ADR-007-automated-release-screenshots.md",
    "docs/testing/PHASE_8_VERIFICATION.md",
    "docs/release/PROJECT_SUMMARY.md",
    "docs/release/RELEASE_NOTES_v1.0.0.md",
    "docs/release/RELEASE_MANIFEST.json",
]

for relative in REQUIRED_FILES:
    if not (ROOT / relative).is_file():
        raise SystemExit(f"Missing Phase 8 release file: {relative}")

manifest = json.loads(
    (ROOT / "docs/release/RELEASE_MANIFEST.json").read_text(encoding="utf-8")
)
if manifest.get("schemaVersion") != "1.0":
    raise SystemExit("Release manifest schemaVersion must be 1.0")
if manifest.get("release") != "v1.0.0":
    raise SystemExit("Release manifest must target v1.0.0")
if manifest.get("readmeScreenshotCount") != 8:
    raise SystemExit("Release manifest must record exactly eight README screenshots")
if manifest.get("performancePassed") is not True:
    raise SystemExit("Release manifest does not record passing performance checks")
if manifest.get("reliabilityReportPresent") is not True:
    raise SystemExit("Release manifest does not record the reliability report")

screenshots = manifest.get("screenshots")
if not isinstance(screenshots, list) or len(screenshots) != 8:
    raise SystemExit("Release manifest must contain exactly eight screenshots")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for marker in [
    "# QueueForge",
    "## Product screenshots",
    "## Architecture",
    "## Reference measurements",
    "## Run locally",
    "All planned phases are complete in `v1.0.0`.",
    "MIT. See [LICENSE](LICENSE).",
]:
    if marker not in readme:
        raise SystemExit(f"Final README section is missing: {marker}")

workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
for marker in [
    "release-verification:",
    "Release verification",
    "Verify Phase 8",
    "python tools/verify_phase_8.py",
    "phase7-performance-results",
]:
    if marker not in workflow:
        raise SystemExit(f"Release workflow integration is missing: {marker}")

for obsolete in [
    "port" + "folio-release:",
    "Final " + "port" + "folio release",
    "phase7-performance-evidence",
]:
    if obsolete in workflow:
        raise SystemExit(f"Obsolete workflow wording remains: {obsolete}")

capture_command = (
    ROOT / "scripts/release/CAPTURE_PRODUCT_SCREENSHOTS.command"
).read_text(encoding="utf-8")
for marker in [
    "mcr.microsoft.com/playwright:v1.55.0-noble",
    "host.docker.internal:host-gateway",
    "QUEUEFORGE_WEB_PORT",
    "restore_normal_stack",
    "tools/screenshots/capture_product_screenshots.cjs",
    "tools/release/render_release_docs.py",
]:
    if marker not in capture_command:
        raise SystemExit(f"Screenshot command is missing: {marker}")

capture = (
    ROOT / "tools/screenshots/capture_product_screenshots.cjs"
).read_text(encoding="utf-8")
for name in [
    "01-product-overview.png",
    "02-scenario-configuration.png",
    "03-live-run-lifecycle.png",
    "04-staffing-comparison.png",
    "05-analytics-json-output.png",
    "06-simulation-kpis.png",
    "07-simulation-json-output.png",
    "08-mobile-interface.png",
]:
    if name not in capture:
        raise SystemExit(f"Screenshot capture contract is missing: {name}")

subprocess.run(
    ["python3", "tools/verify_release_screenshots.py"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    ["python3", "tools/quality/verify_public_metadata.py"],
    cwd=ROOT,
    check=True,
)

tracked = subprocess.run(
    ["git", "ls-files", "docs/assets/readme"],
    cwd=ROOT,
    check=True,
    text=True,
    capture_output=True,
).stdout.splitlines()

if len(tracked) != 8:
    raise SystemExit(
        f"Git must track exactly eight README screenshots, found {len(tracked)}"
    )
if any(not path.endswith(".png") for path in tracked):
    raise SystemExit("README screenshot directory contains a tracked non-PNG file")

print(f"Phase 8 release verification passed ({len(REQUIRED_FILES)} required files).")
