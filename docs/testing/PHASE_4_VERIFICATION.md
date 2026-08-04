# Phase 4 Verification

## Java unit tests

The Maven build checks:

- lifecycle terminal-state classification
- scenario validation and analytics defaults
- invalid triangular service parameters
- simulation command construction
- analytics command construction
- system readiness reporting

## Docker integration

Run:

```bash
./VERIFY_PHASE_4.command
```

The fixed demonstration:

1. builds one API image containing Java, Python and C++
2. starts PostgreSQL and applies Flyway migration V1
3. verifies database and worker readiness
4. submits an asynchronous C++ simulation
5. polls to `SUCCEEDED` and verifies invariants
6. submits a 15-run Python analytics experiment
7. verifies the stored analytics report
8. rejects an invalid scenario with HTTP 400 Problem Details
9. cancels a deliberately long analytics run
10. restarts the API container
11. proves the completed run remains in PostgreSQL

## CI

GitHub Actions keeps the existing language jobs and adds a control-plane integration job using Docker Compose.

## Known limits

- one API instance owns all active processes
- there is no authentication in v1
- there is no message broker
- result JSON is stored as a document rather than decomposed metrics
- cancellation is cooperative at the API level and forceful at the OS process level
