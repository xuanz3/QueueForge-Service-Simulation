# ADR-006: Use Portable Regression Budgets

## Status

Accepted.

## Context

QueueForge runs on different laptops and GitHub-hosted runners. Tight absolute
latency targets would mostly measure hardware, Docker startup and host load.

## Decision

Use portable regression budgets for:

- C++ deterministic simulation latency
- Python analytics wall time
- API submission and completion latency
- success ratio under bounded concurrency
- Web bundle sizes
- Docker image sizes

The benchmark records actual measurements and environment metadata. A budget
failure blocks the Phase 7 gate, but passing a budget is not presented as a
production capacity guarantee.

## Consequences

The project gains repeatable regression protection without inventing a
production-scale claim. Future releases can tighten budgets only after multiple
comparable baselines exist.
