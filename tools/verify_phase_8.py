from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "compose.portfolio.yaml",
    "GENERATE_PORTFOLIO_EVIDENCE.command",
    "VERIFY_PHASE_8.command",
    "tools/evidence/capture_portfolio.cjs",
    "tools/evidence/render_release_docs.py",
    "tools/verify_phase_8.py",
    "tools/verify_phase_8_assets.py",
    "docs/decisions/ADR-007-automated-portfolio-evidence.md",
    "docs/testing/PHASE_8_VERIFICATION.md",
    "docs/release/PORTFOLIO_SUMMARY.md",
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
if manifest.get("readmeImageCount") != 8:
    raise SystemExit("Release manifest must record exactly eight README images")
if manifest.get("performancePassed") is not True:
    raise SystemExit("Release manifest does not record passing performance gates")
if manifest.get("reliabilityEvidencePresent") is not True:
    raise SystemExit("Release manifest does not record reliability evidence")

images = manifest.get("images")
if not isinstance(images, list) or len(images) != 8:
    raise SystemExit("Release manifest image list must contain exactly eight items")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for marker in [
    "# QueueForge",
    "## Product evidence",
    "## Architecture",
    "## Reference verification",
    "## Run locally",
    "All phases are complete in `v1.0.0`.",
    "MIT. See [LICENSE](LICENSE).",
]:
    if marker not in readme:
        raise SystemExit(f"Final README section is missing: {marker}")

workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
for marker in [
    "portfolio-release:",
    "Final portfolio release",
    "Verify Phase 8",
    "python tools/verify_phase_8.py",
]:
    if marker not in workflow:
        raise SystemExit(f"Final release workflow integration is missing: {marker}")

generator = (ROOT / "GENERATE_PORTFOLIO_EVIDENCE.command").read_text(
    encoding="utf-8"
)
for marker in [
    "mcr.microsoft.com/playwright:v1.55.0-noble",
    "host.docker.internal:host-gateway",
    "QUEUEFORGE_WEB_PORT",
    "restore_normal_stack",
    "tools/evidence/capture_portfolio.cjs",
]:
    if marker not in generator:
        raise SystemExit(f"Portfolio generator is missing: {marker}")

capture = (ROOT / "tools/evidence/capture_portfolio.cjs").read_text(
    encoding="utf-8"
)
for name in [
    "01-product-overview.png",
    "02-scenario-configuration.png",
    "03-live-run-lifecycle.png",
    "04-staffing-comparison.png",
    "05-analytics-json-evidence.png",
    "06-simulation-kpis.png",
    "07-simulation-json-evidence.png",
    "08-mobile-interface.png",
]:
    if name not in capture:
        raise SystemExit(f"Screenshot capture contract is missing: {name}")

subprocess.run(
    ["python3", "tools/verify_phase_8_assets.py"],
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
        f"Git must track exactly eight README assets, found {len(tracked)}"
    )

if any(not path.endswith(".png") for path in tracked):
    raise SystemExit("README asset directory contains a tracked non-PNG file")

print(f"Phase 8 final release verification passed ({len(REQUIRED_FILES)} required files).")
