# Performance Method

Phase 7 measures regression budgets through the normal Docker product stack.

## Workloads

### C++ engine

- basic versioned scenario
- 25 executions inside the API container
- median and p95 wall time
- SHA-256 comparison of canonical JSON results
- identical results required for the fixed seed

### Python analytics

- server counts 3, 4 and 5
- 20 runs per server count
- fixed seed start `20260801`
- real packaged C++ engine
- staffing comparison report must be generated

### Java API

- 12 simulation lifecycles
- concurrency of 4
- bounded admission remains active
- successful completion ratio
- submit p95 and end-to-end p95

### React and containers

- production JavaScript bytes
- production CSS bytes
- API image bytes
- Web image bytes

## Evidence

The benchmark writes:

```text
runtime/phase7/performance-report.json
runtime/phase7/performance-report.md
runtime/phase7/staffing-comparison.json
```

CI uploads the Phase 7 runtime directory as an artifact.

## Interpretation

Budgets protect against large accidental regressions. They do not represent a
production SLO, cloud capacity result or hardware-independent guarantee.
