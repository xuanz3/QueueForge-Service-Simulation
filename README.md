# QueueForge

> A local-first service operations simulator that helps teams evaluate queue behaviour and staffing decisions before changing real operations.

QueueForge combines a deterministic C++20 simulation engine, Python multi-seed analytics and a Java control plane that persists and supervises worker execution.

## Current status

**Phase 5 — React Product Interface**

Implemented evidence:

- asynchronous simulation and analytics REST API
- PostgreSQL run lifecycle persistence
- Flyway database migration
- Java validation of versioned scenario input
- bounded C++ and Python process orchestration
- timeout, cancellation and restart recovery
- stable lifecycle states and error codes
- completed result retrieval after API restart
- Docker integration testing across all three languages

The application now supports an end-to-end local product workflow. Reliability hardening and failure injection belong to Phase 6.

## Run the control-plane demo

Start Docker Desktop, then run:

```bash
./VERIFY_PHASE_4.command
```

API endpoints:

```text
GET  http://localhost:18086/api/system/status
POST http://localhost:18086/api/runs
GET  http://localhost:18086/api/runs/{id}
GET  http://localhost:18086/api/runs/{id}/result
POST http://localhost:18086/api/runs/{id}/cancel
```

Generated integration evidence is written to:

```text
runtime/phase4/
```

## Product interface

Open `http://localhost:15176` after running:

```bash
./VERIFY_PHASE_5.command
```

The interface configures real versioned scenarios, submits simulation or
analytics runs, follows persisted lifecycle state, supports cancellation and
renders the returned evidence.

## Architecture responsibilities

| Component | Responsibility |
|---|---|
| C++20 | Deterministic event simulation |
| Python | Repeated experiments, uncertainty and reports |
| Java / Spring Boot | Validation, lifecycle, process control and persistence |
| PostgreSQL | Durable run metadata, request and result evidence |
| React / TypeScript | Scenario configuration and result review |

## Evidence

- [Control-plane architecture](docs/architecture/CONTROL_PLANE.md)
- [Local process orchestration decision](docs/decisions/ADR-005-local-process-orchestration.md)
- [Run lifecycle](docs/operations/RUN_LIFECYCLE.md)
- [Phase 4 verification](docs/testing/PHASE_4_VERIFICATION.md)
- [Python experiment method](docs/analytics/EXPERIMENT_METHOD.md)
- [C++ engine design](docs/architecture/ENGINE_DESIGN.md)

## Planned phases

1. Product definition — complete
2. Repository and local environment — complete
3. C++ simulation engine — complete
4. Python analytics — complete
5. Java control plane — complete
6. React product interface — in review
7. Reliability and fault handling
8. Quality and performance
9. Portfolio release

## Evidence policy

Performance, reliability and staffing claims are published only with their input, engine version, seed schedule, environment and limitations.
