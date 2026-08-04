# QueueForge Project Summary

## Product

QueueForge is a complete local-first service operations simulator. A user can
configure a queue scenario, execute one deterministic simulation or compare
staffing options across repeated runs, observe the durable lifecycle and inspect
versioned JSON output.

## Engineering coverage

- C++20 discrete-event simulation
- Python experiment orchestration and statistics
- Java 21 / Spring Boot REST control plane
- PostgreSQL persistence and Flyway migration
- React and TypeScript product interface
- Docker multi-stage builds and Compose integration
- GitHub Actions across unit, integration, reliability and performance gates
- Micrometer, Actuator and Prometheus telemetry
- Playwright evidence automation

## Verified reference results

- deterministic C++ output: pass
- C++ p95: 2.854 ms
- Python analytics: 0.541 s
- API success rate: 100%
- API end-to-end p95: 202.235 ms
- final README screenshots: 8

## Reliability checks

The automated suite verifies bounded admission, HTTP 429, worker exit,
worker timeout, API restart reconciliation and restoration of a successful
normal simulation.

## Review path

A reviewer can understand the project in this order:

1. README product screenshots
2. architecture responsibilities
3. reliability model
4. quality and performance method
5. phase-based PR and Issue history
6. v1.0.0 release
