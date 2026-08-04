from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "apps/web/src/domain.ts",
    "apps/web/src/api.ts",
    "apps/web/src/scenario.ts",
    "apps/web/src/App.tsx",
    "apps/web/src/styles.css",
    "apps/web/nginx.conf",
    "docs/product/PHASE_5_PRODUCT_INTERFACE.md",
    "docs/testing/PHASE_5_VERIFICATION.md",
    "docs/testing/INCIDENT-007-PHASE5-VERIFIER-AND-SERVING.md",
    "docs/testing/INCIDENT-008-TYPESCRIPT-GENERIC-SPREAD.md",
    "docs/testing/INCIDENT-009-WEB-RUNTIME-404.md",
    "docs/testing/INCIDENT-010-TYPECHECK-IN-NGINX.md",
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


dockerfile = (ROOT / "apps/web/Dockerfile").read_text(encoding="utf-8")
for required in [
    "FROM node:24-alpine AS build",
    "ARG VITE_API_BASE_URL=http://localhost:18086",
    "RUN npm run build",
    "FROM nginx:1.27-alpine",
    "COPY --from=build /app/dist /usr/share/nginx/html",
    'CMD ["nginx", "-g", "daemon off;"]',
]:
    if required not in dockerfile:
        raise SystemExit(f"Production web image is missing: {required}")

nginx = (ROOT / "apps/web/nginx.conf").read_text(encoding="utf-8")
for required in [
    "listen 5173;",
    "root /usr/share/nginx/html;",
    "try_files $uri $uri/ /index.html;",
]:
    if required not in nginx:
        raise SystemExit(f"Nginx configuration is missing: {required}")

compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
for required in [
    "args:",
    "VITE_API_BASE_URL: http://localhost:${QUEUEFORGE_API_PORT:-18086}",
]:
    if required not in compose:
        raise SystemExit(f"Compose web build is missing: {required}")

demo = (ROOT / "RUN_PRODUCT_UI_DEMO.command").read_text(encoding="utf-8")
for required in [
    "docker compose rm -sf web",
    "docker compose up -d --build --force-recreate postgres api web",
]:
    if required not in demo:
        raise SystemExit(f"Product UI runtime reset is missing: {required}")

dockerfile = (ROOT / "apps/web/Dockerfile").read_text(encoding="utf-8")
for required in [
    "FROM build AS typecheck",
    "RUN npm run typecheck",
]:
    if required not in dockerfile:
        raise SystemExit(f"Typecheck build stage is missing: {required}")

phase5_command = (ROOT / "VERIFY_PHASE_5.command").read_text(encoding="utf-8")
for required in [
    "--target typecheck",
    "queueforge-web-typecheck:phase5",
    "apps/web",
]:
    if required not in phase5_command:
        raise SystemExit(f"Phase 5 typecheck command is missing: {required}")

if "docker compose run --rm -T --no-deps web npm run typecheck" in phase5_command:
    raise SystemExit("Phase 5 attempts to run npm inside the Nginx service")

print(f"Phase 5 repository verification passed ({len(REQUIRED_FILES)} required files).")
