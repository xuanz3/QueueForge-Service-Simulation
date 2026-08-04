from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "apps/web/src/domain.ts",
    "apps/web/src/api.ts",
    "apps/web/src/scenario.ts",
    "apps/web/src/App.tsx",
    "apps/web/src/styles.css",
    "docs/product/PHASE_5_PRODUCT_INTERFACE.md",
    "docs/testing/PHASE_5_VERIFICATION.md",
    "tools/verify_phase_5_runtime.py",
    "RUN_PRODUCT_UI_DEMO.command",
    "VERIFY_PHASE_5.command",
]

for relative in REQUIRED_FILES:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"Missing Phase 5 file: {relative}")

app = (ROOT / "apps/web/src/App.tsx").read_text(encoding="utf-8")
api = (ROOT / "apps/web/src/api.ts").read_text(encoding="utf-8")
scenario = (ROOT / "apps/web/src/scenario.ts").read_text(encoding="utf-8")
styles = (ROOT / "apps/web/src/styles.css").read_text(encoding="utf-8")

for marker in [
    "QueueForge",
    "Operations studio",
    "Staffing analysis",
    "Compare staffing options",
    "Cancel run",
    "SimulationResult",
    "AnalyticsResult",
    "controlPlaneApi.createRun",
    "controlPlaneApi.cancelRun",
]:
    if marker not in app:
        raise SystemExit(f"Product interface is missing marker: {marker}")

for endpoint in [
    "/api/system/status",
    "/api/runs",
    "/cancel",
    "/result",
]:
    if endpoint not in api:
        raise SystemExit(f"Typed API client is missing endpoint: {endpoint}")

for marker in [
    "validateScenario",
    "validateAnalytics",
    "minimum <= mode",
    "serverCounts",
]:
    if marker not in scenario:
        raise SystemExit(f"Scenario contract is missing marker: {marker}")

for marker in [
    ".workspace",
    ".run-sidebar",
    ".metrics-grid",
    "@media (max-width: 680px)",
]:
    if marker not in styles:
        raise SystemExit(f"Responsive styling is missing marker: {marker}")

for forbidden in ["dangerouslySetInnerHTML", "Math.random()", "mockResult", "fakeResult"]:
    if forbidden in app:
        raise SystemExit(f"Product interface contains forbidden pattern: {forbidden}")

print(f"Phase 5 repository verification passed ({len(REQUIRED_FILES)} required files).")
