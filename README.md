# QueueForge

> A local-first service operations simulator that helps teams evaluate queue behaviour and staffing decisions before changing real operations.

QueueForge models a fictional Melbourne community service centre. A deterministic C++20 engine produces auditable queue simulations, while Python runs repeated experiments and reports uncertainty across staffing options.

## Current status

**Phase 3 — Python Analytics**

Implemented evidence:

- deterministic C++20 discrete-event simulation
- 40 common seeds per staffing variant
- 3, 4 and 5 server comparison
- run-level metrics and engine invariant validation
- means, standard deviations and 95% confidence intervals
- explicit demonstration target policy
- analytical arrival and offered-load reasonableness checks
- JSON, summary CSV, run-level CSV and local HTML reports
- Python unit tests and C++ integration CI

The fixed synthetic demonstration selects four servers because it is the lowest tested variant whose observed success rate reaches 90%. This is not operational staffing advice.

## Run the analytics demo

Start Docker Desktop, then run:

```bash
./VERIFY_PHASE_3.command
```

Open the generated report:

```text
runtime/phase3/staffing-report.html
```

## Fixed demonstration evidence

| Servers | Target success rate | Mean run P95 wait | Mean maximum queue | Mean utilisation |
|---:|---:|---:|---:|---:|
| 3 | 2.5% | 24.912 min | 11.950 | 88.8% |
| 4 | 92.5% | 5.811 min | 5.425 | 68.5% |
| 5 | 100.0% | 2.002 min | 3.475 | 53.9% |

These figures apply only to the committed basic scenario, engine version 0.2.0 and seeds 20260801–20260840.

## Architecture responsibilities

| Component | Responsibility |
|---|---|
| C++20 | Deterministic event simulation and performance evidence |
| Python | Repeated experiments, statistics, decision rules and reports |
| Java / Spring Boot | Validation, lifecycle, process control and persistence |
| React / TypeScript | Scenario configuration and result review |

## Evidence

- [Experiment method](docs/analytics/EXPERIMENT_METHOD.md)
- [Common random numbers decision](docs/decisions/ADR-004-common-random-numbers.md)
- [Phase 3 verification](docs/testing/PHASE_3_VERIFICATION.md)
- [Engine design](docs/architecture/ENGINE_DESIGN.md)
- [Analytics report contract](contracts/schemas/analytics-report.schema.json)

## Planned phases

1. Product definition — complete
2. Repository and local environment — complete
3. C++ simulation engine — complete
4. Python analytics — in review
5. Java control plane
6. React product interface
7. Reliability and fault handling
8. Quality and performance
9. Portfolio release

## Evidence policy

Performance, reliability and staffing claims are published only with their input, engine version, seed schedule, environment and limitations.
