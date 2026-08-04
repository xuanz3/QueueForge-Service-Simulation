# Changelog

All notable changes to QueueForge are documented here.

## Unreleased

### Changed

- standardised public release and screenshot terminology
- improved README screenshot framing and mobile layout
- upgraded GitHub Actions to Node 24-compatible major versions
- simplified project, release and contribution documentation

## [1.0.0] - 2026-08-05

### Added

- deterministic C++20 discrete-event queue simulation
- Python multi-seed staffing analytics and report generation
- Java 21 / Spring Boot run control plane
- PostgreSQL lifecycle persistence and Flyway migration
- React / TypeScript product interface
- bounded run admission and structured HTTP 429 responses
- worker cancellation, timeout and restart reconciliation
- Actuator readiness and Prometheus telemetry
- cross-language quality and performance regression checks
- automated Playwright product screenshot capture
- eight-image README and GitHub release workflow

### Verified

- fixed-seed deterministic output
- C++ release, sanitizer and warnings-as-errors builds
- Python unit and C++ integration tests
- Java unit and full lifecycle integration tests
- real React-to-API product workflow
- capacity, failure, timeout and restart fault injection
- ten performance and size checks
- exact README screenshot contract
