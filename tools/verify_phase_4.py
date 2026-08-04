#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunType.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunStatus.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/CreateRunRequest.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/NormalizedRunRequest.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunRecord.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunRepository.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/ScenarioValidator.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/WorkerCommandFactory.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/WorkerProcessRunner.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunService.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunController.java",
    "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/ApiExceptionHandler.java",
    "services/control-plane-java/src/main/resources/db/migration/V1__create_queueforge_runs.sql",
    "RUN_CONTROL_PLANE_DEMO.command",
    "VERIFY_PHASE_4.command",
    "docs/architecture/CONTROL_PLANE.md",
    "docs/decisions/ADR-005-local-process-orchestration.md",
    "docs/operations/RUN_LIFECYCLE.md",
    "docs/testing/PHASE_4_VERIFICATION.md",
    "services/control-plane-java/src/test/java/dev/queueforge/controlplane/run/RunServiceContextTest.java",
    "docs/testing/INCIDENT-002-SPRING-CONSTRUCTOR-SELECTION.md",
]

missing = [item for item in REQUIRED_FILES if not (ROOT / item).is_file()]
if missing:
    raise SystemExit("Missing Phase 4 files:\n" + "\n".join(f"- {item}" for item in missing))

for relative in ["RUN_CONTROL_PLANE_DEMO.command", "VERIFY_PHASE_4.command"]:
    if not os.access(ROOT / relative, os.X_OK):
        raise SystemExit(f"Phase 4 command is not executable: {relative}")

pom = (ROOT / "services/control-plane-java/pom.xml").read_text(encoding="utf-8")
for dependency in [
    "spring-boot-starter-validation",
    "spring-boot-starter-flyway",
    "flyway-database-postgresql",
]:
    if dependency not in pom:
        raise SystemExit(f"Java control plane is missing dependency: {dependency}")

compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
for setting in [
    "dockerfile: services/control-plane-java/Dockerfile",
    "QUEUEFORGE_WORK_ROOT: /var/lib/queueforge/runs",
    "queueforge-runs:/var/lib/queueforge/runs",
]:
    if setting not in compose:
        raise SystemExit(f"compose.yaml is missing Phase 4 setting: {setting}")

migration = (
    ROOT
    / "services/control-plane-java/src/main/resources/db/migration/V1__create_queueforge_runs.sql"
).read_text(encoding="utf-8")
for state in ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]:
    if state not in migration:
        raise SystemExit(f"Run migration is missing lifecycle state: {state}")

command_factory = (
    ROOT
    / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/WorkerCommandFactory.java"
).read_text(encoding="utf-8")
if "ProcessBuilder" in command_factory or "sh -c" in command_factory or "bash -c" in command_factory:
    raise SystemExit("Worker commands must be argument lists without shell interpolation")

process_runner = (
    ROOT
    / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/WorkerProcessRunner.java"
).read_text(encoding="utf-8")
for control in ["WORKER_TIMEOUT", "WorkerCancelledException", "destroyForcibly"]:
    if control not in process_runner:
        raise SystemExit(f"Worker runner is missing lifecycle control: {control}")


run_service = (
    ROOT
    / "services/control-plane-java/src/main/java/dev/queueforge/controlplane/run/RunService.java"
).read_text(encoding="utf-8")

if "import org.springframework.beans.factory.annotation.Autowired;" not in run_service:
    raise SystemExit("RunService is missing the Autowired constructor import")

production_signature = (
    "    @Autowired\n"
    "    public RunService(\n"
    "            RunRepository repository,\n"
    "            ScenarioValidator validator,\n"
    "            WorkerProcessRunner workerRunner,\n"
    "            JsonMapper jsonMapper,\n"
    "            ExecutorService executor) {"
)

if production_signature not in run_service:
    raise SystemExit("RunService production constructor is not explicitly autowired")

context_test = (
    ROOT
    / "services/control-plane-java/src/test/java/dev/queueforge/controlplane/run/"
    "RunServiceContextTest.java"
).read_text(encoding="utf-8")

for required in [
    "AnnotationConfigApplicationContext",
    "context.registerBean(RunService.class)",
    "context.refresh()",
    "context.getBean(RunService.class)",
]:
    if required not in context_test:
        raise SystemExit(
            f"RunService context regression test is missing requirement: {required}"
        )

print(f"Phase 4 repository verification passed ({len(REQUIRED_FILES)} required files).")
