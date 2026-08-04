# QueueForge

> A local-first service operations simulator that helps teams evaluate queue behaviour and staffing decisions before changing real operations.

QueueForge models a fictional Melbourne community service centre. It uses repeatable discrete-event simulation to compare queue behaviour and staffing assumptions before any real operational change is made.

## Current status

**Phase 2 — C++ Simulation Engine**

The repository now contains:

- a C++20 discrete-event simulation engine
- deterministic random generation from an explicit seed
- FIFO and priority-FIFO waiting queues
- multiple service staff
- Poisson arrivals and triangular service durations
- versioned JSON input and result contracts
- event timelines, waiting-time metrics and utilisation
- accounting, chronology and utilisation invariants
- release, sanitizer and runtime-container checks

No staffing recommendation is claimed yet. Statistical multi-seed comparison belongs to Phase 3.

## Run the engine demo

Start Docker Desktop, then run:

```bash
./VERIFY_PHASE_2.command
```

Generated local results are written to:

```text
runtime/phase2/
```

The verification checks:

- identical input and seed produce identical JSON
- all simulation invariants hold
- an overloaded scenario forms a queue
- malformed service parameters return exit code 65
- the final Docker image can execute the engine

## CLI

```bash
queueforge-sim \
  --input scenario.json \
  --output result.json \
  --pretty
```

Validate a contract without running a simulation:

```bash
queueforge-sim \
  --input scenario.json \
  --output - \
  --validate-only
```

## Language responsibilities

| Component | Responsibility |
|---|---|
| C++20 | Deterministic event simulation and performance evidence |
| Python | Repeated experiments, statistics and reports |
| Java / Spring Boot | Validation, lifecycle, process control and persistence |
| React / TypeScript | Scenario configuration and result review |

## Evidence

- [Engine design](docs/architecture/ENGINE_DESIGN.md)
- [Deterministic randomness decision](docs/decisions/ADR-003-deterministic-randomness.md)
- [Phase 2 verification](docs/testing/PHASE_2_VERIFICATION.md)
- [C++ runtime ABI incident](docs/testing/INCIDENT-001-CPP-RUNTIME-ABI.md)
- [Input schema](contracts/schemas/simulation-input.schema.json)
- [Result schema](contracts/schemas/simulation-result.schema.json)

## Planned phases

1. Product definition — complete
2. Repository and local environment — complete
3. C++ simulation engine — in review
4. Python analytics
5. Java control plane
6. React product interface
7. Reliability and fault handling
8. Quality and performance
9. Portfolio release

## Evidence policy

Performance, reliability and staffing claims are published only after the corresponding scripts, inputs, environment details and tests are committed.
