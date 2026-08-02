# QueueForge

> A local-first service operations simulator that helps teams evaluate queue behaviour and staffing decisions before changing real operations.

## Current status

**Phase 1 — Repository Foundation**

The independently testable foundation now contains:

- C++20 and CMake simulation-engine executable
- Python 3.14 analytics package
- Java 21 and Spring Boot control plane
- PostgreSQL connectivity
- React, TypeScript and Vite interface
- Docker Compose and GitHub Actions verification

No simulation or staffing result is claimed yet.

## Run locally

```bash
./START_LOCAL.command
```

- Web: `http://localhost:15176`
- API: `http://localhost:18086/api/system/status`
- PostgreSQL: `localhost:55436`

Complete verification:

```bash
./VERIFY_PHASE_1.command
```

## Language responsibilities

| Component | Planned responsibility |
|---|---|
| C++20 | Deterministic event simulation and performance evidence |
| Python | Repeated experiments, statistics and reports |
| Java / Spring Boot | Validation, lifecycle, process control and persistence |
| React / TypeScript | Scenario configuration and result review |

See `docs/` for the product scope, architecture decisions, assumptions, evidence plan and definition of done.
