# Phase 6 Verification

Run:

```bash
./VERIFY_PHASE_6.command
```

The gate validates all repository contracts from Phases 0–6 and performs
deterministic runtime failures.

| Test | Expected result |
|---|---|
| Normal simulation | `SUCCEEDED` |
| Third request with two slots occupied | HTTP 429 and `Retry-After: 2` |
| Worker exits with code 23 | `FAILED / WORKER_EXIT_23` |
| Worker exceeds two-second timeout | `FAILED / WORKER_TIMEOUT` |
| API restarts during active work | `FAILED / CONTROL_PLANE_RESTARTED` |
| Stack restored to normal | New simulation `SUCCEEDED` |

It also checks Actuator readiness, Prometheus metric names, browser-origin
CORS, the production React bundle and healthy final containers.

Evidence:

```text
runtime/phase6/reliability-evidence.json
```
