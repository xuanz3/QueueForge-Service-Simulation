from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "apps/web/src/domain.ts",
    "apps/web/src/api.ts",
    "apps/web/src/scenario.ts",
    "apps/web/src/App.tsx",
    "apps/web/src/styles.css",
    "docs/product/PHASE_5_PRODUCT_INTERFACE.md",
    "docs/testing/PHASE_5_VERIFICATION.md",
    "docs/testing/INCIDENT-007-PHASE5-VERIFIER-AND-SERVING.md",
    "docs/testing/INCIDENT-008-TYPESCRIPT-GENERIC-SPREAD.md",
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
    "minimumMinutes <= modeMinutes",
    "modeMinutes <= maximumMinutes",
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

package = json.loads((ROOT / "apps/web/package.json").read_text(encoding="utf-8"))
if package.get("scripts", {}).get("preview") != "vite preview --host 0.0.0.0 --port 5173":
    raise SystemExit("Web package is missing the production preview command")

dockerfile = (ROOT / "apps/web/Dockerfile").read_text(encoding="utf-8")
if 'CMD ["npm", "run", "preview"]' not in dockerfile:
    raise SystemExit("Web container does not serve the production Vite build")

workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
if "working-directory: ../.." in workflow:
    raise SystemExit("TypeScript CI contains an unsafe parent working directory")


for required in [
    'const updateSimulation = (',
    'Partial<Scenario["simulation"]>',
    'const updateArrivals = (',
    'Partial<Scenario["arrivals"]>',
    'const updateService = (',
    'Partial<Scenario["service"]>',
    'const updateQueue = (',
    'Partial<Scenario["queue"]>',
]:
    if required not in app:
        raise SystemExit(f"Typed scenario updater is missing: {required}")

for forbidden in [
    "const updateScenario = <K extends keyof Scenario>",
    "[section]: { ...current[section], ...values }",
]:
    if forbidden in app:
        raise SystemExit(f"Generic scenario spread is forbidden: {forbidden}")

print(f"Phase 5 repository verification passed ({len(REQUIRED_FILES)} required files).")
