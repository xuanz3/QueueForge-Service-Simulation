# QueueForge

> A local-first service operations simulator that helps teams evaluate queue behaviour and staffing decisions before changing real operations.

QueueForge models a fictional Melbourne community service centre. It allows an analyst to configure arrivals, service-time distributions, staffing levels and queue discipline, then compare repeatable simulation results across staffing options.

## Why this project exists

Operational teams often need to answer questions such as:

- How many staff members are required during a peak period?
- Which configuration meets a waiting-time target without excessive idle capacity?
- How sensitive is the decision to random variation?
- Can the result be reproduced and audited later?

QueueForge is designed around those decisions rather than around a generic queue animation.

## Technical responsibilities

| Component | Responsibility |
|---|---|
| C++20 simulation engine | Deterministic event scheduling, queues, servers, metrics and benchmarks |
| Python analytics | Multi-seed experiments, statistical comparison and report generation |
| Java / Spring Boot control plane | Validation, run lifecycle, process orchestration and PostgreSQL persistence |
| React / TypeScript interface | Scenario configuration, timelines, comparisons and result review |
| JSON Schema contract | Versioned cross-language input and output boundary |

The first implementation deliberately uses local processes and versioned JSON files instead of distributed messaging. This keeps failures observable and the project reproducible while still demonstrating a real polyglot boundary.

## Planned evidence

- Deterministic simulations using explicit random seeds
- Cross-checking between the C++ engine and a readable Python reference model
- Failure, timeout and cancellation handling in Java
- Repeated staffing experiments with uncertainty reported
- Measured performance evidence rather than invented claims
- Automated tests across C++, Python, Java and TypeScript
- Eight reproducible README images generated from fixed demo data

## Current phase

**Phase 0 — Product Definition**

This phase freezes the v1.0 scope, terminology, metrics, technical boundaries and acceptance criteria before implementation.

See:

- [Project brief](docs/product/PROJECT_BRIEF.md)
- [v1.0 scope](docs/product/SCOPE.md)
- [User stories](docs/product/USER_STORIES.md)
- [Metrics and assumptions](docs/product/METRICS_AND_ASSUMPTIONS.md)
- [System context](docs/architecture/SYSTEM_CONTEXT.md)
- [Definition of done](docs/testing/DEFINITION_OF_DONE.md)
- [Screenshot evidence plan](docs/portfolio/SCREENSHOT_PLAN.md)
- [Zero-cost policy](docs/operations/ZERO_COST_POLICY.md)

## Planned phases

1. Product definition
2. Repository and local environment
3. C++ simulation engine
4. Python analytics
5. Java control plane
6. React product interface
7. Reliability and fault handling
8. Quality and performance
9. Portfolio release

## Status

No performance, reliability or staffing result is claimed yet. Results will only be published after the corresponding scripts and test conditions are committed.
