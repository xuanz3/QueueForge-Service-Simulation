# QueueForge Project Summary

## Purpose

QueueForge tests queue and staffing decisions through a reproducible local
simulation workflow. Users can run one deterministic scenario or compare
staffing options across repeated seeds, then inspect the persisted lifecycle and
versioned JSON output.

## Engineering scope

- C++20 discrete-event simulation
- Python experiment orchestration and statistics
- Java 21 / Spring Boot REST control plane
- PostgreSQL persistence and Flyway migration
- React and TypeScript product interface
- Docker multi-stage builds and Compose integration
- GitHub Actions for unit, integration, reliability and performance checks
- Micrometer, Actuator and Prometheus telemetry
- Playwright screenshot automation

## Reference results

- deterministic C++ output: pass
- C++ p95: 1.901 ms
- Python analytics: 0.586 s
- API success rate: 100%
- API end-to-end p95: 199.79 ms
- README screenshots: 8

## Reliability checks

The automated suite covers bounded admission, HTTP 429 responses, worker exit,
worker timeout, API restart reconciliation and restoration of a successful
normal simulation.

## Operating boundary

QueueForge is intended for local evaluation with fictional scenarios. It is not
a distributed job platform or an operational staffing recommendation system.
