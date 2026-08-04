from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/WorkerReadinessHealthIndicator.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunAdmissionController.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunCapacityException.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunTelemetry.java",
    "services/control-plane-java/src/test/java/dev/queueforge/controlplane/run/RunAdmissionControllerTest.java",
    "services/control-plane-java/src/test/java/dev/queueforge/controlplane/run/RunTelemetryTest.java",
    "tools/faults/slow-simulation.sh",
    "tools/faults/failing-simulation.sh",
    "tools/faults/hanging-simulation.sh",
    "tools/verify_phase_6_runtime.py",
    "docs/architecture/RELIABILITY_MODEL.md",
    "docs/operations/RELIABILITY_PLAYBOOK.md",
    "docs/testing/PHASE_6_VERIFICATION.md",
    "docs/testing/INCIDENT-011-STALE-RUNSERVICE-SIGNATURE-VERIFIER.md",
    "VERIFY_PHASE_6.command",
]

for relative in REQUIRED_FILES:
    if not (ROOT / relative).is_file():
        raise SystemExit(f"Missing Phase 6 file: {relative}")

service = (ROOT / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunService.java").read_text(encoding="utf-8")
handler = (ROOT / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/ApiExceptionHandler.java").read_text(encoding="utf-8")
settings = (ROOT / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/WorkerSettings.java").read_text(encoding="utf-8")
application = (ROOT / "services/control-plane-java/src/main/resources/application.yml").read_text(encoding="utf-8")
compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
dockerfile = (ROOT / "services/control-plane-java/Dockerfile").read_text(encoding="utf-8")
runtime = (ROOT / "tools/verify_phase_6_runtime.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")

for marker in [
    "admission.tryAcquire()",
    "telemetry.rejected()",
    "throw new RunCapacityException",
    "admission.release()",
]:
    if marker not in service:
        raise SystemExit(f"Run admission lifecycle is missing: {marker}")

for marker in [
    "HttpStatus.TOO_MANY_REQUESTS",
    'header(HttpHeaders.RETRY_AFTER, "2")',
    'detail.setProperty("capacity"',
]:
    if marker not in handler:
        raise SystemExit(f"Capacity Problem Detail is missing: {marker}")

for marker in [
    "int queueCapacity",
    "maxOutstandingRuns()",
]:
    if marker not in settings:
        raise SystemExit(f"Worker capacity setting is missing: {marker}")

for marker in [
    "health,info,flyway,metrics,prometheus",
    "queue-capacity:",
    "queueforgeWorkers",
]:
    if marker not in application:
        raise SystemExit(f"Actuator reliability configuration is missing: {marker}")

for marker in [
    "QUEUEFORGE_WORKER_QUEUE_CAPACITY",
    "QUEUEFORGE_FAULT_DELAY_SECONDS",
    "condition: service_healthy",
]:
    if marker not in compose:
        raise SystemExit(f"Compose reliability configuration is missing: {marker}")

for marker in [
    "COPY tools/faults /opt/queueforge-faults",
    "chmod 0555 /opt/queueforge-faults/*.sh",
]:
    if marker not in dockerfile:
        raise SystemExit(f"API image fault tooling is missing: {marker}")

for marker in [
    "Run capacity exhausted",
    "WORKER_EXIT_23",
    "WORKER_TIMEOUT",
    "CONTROL_PLANE_RESTARTED",
    "reliability-evidence.json",
]:
    if marker not in runtime:
        raise SystemExit(f"Fault verification is missing: {marker}")

if "python tools/verify_phase_6.py" not in workflow:
    raise SystemExit("Repository CI does not verify Phase 6")
if "reliability-integration:" not in workflow:
    raise SystemExit("Quality workflow is missing the Phase 6 reliability job")

phase4_verifier = (ROOT / "tools/verify_phase_4.py").read_text(encoding="utf-8")
for required in [
    "autowired_constructor_start",
    "RunAdmissionController admission",
    "RunTelemetry telemetry",
]:
    if required not in phase4_verifier:
        raise SystemExit(f"Constructor verifier compatibility is missing: {required}")

if "production_signature = (" in phase4_verifier:
    raise SystemExit("Phase 4 still pins the historical RunService signature")

print(f"Phase 6 repository verification passed ({len(REQUIRED_FILES)} required files).")
