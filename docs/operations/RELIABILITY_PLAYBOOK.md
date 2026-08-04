# Reliability Playbook

## Readiness

```bash
curl http://localhost:18086/actuator/health/readiness
```

## Capacity

```bash
curl http://localhost:18086/api/system/status
```

The `capacity` object reports maximum, admitted and available run slots.
Capacity exhaustion returns HTTP 429 and `Retry-After: 2`.

## Metrics

```bash
curl http://localhost:18086/actuator/prometheus
```

Key series:

- `queueforge_runs_active`
- `queueforge_runs_submitted_total`
- `queueforge_runs_rejected_total`
- `queueforge_runs_succeeded_total`
- `queueforge_runs_failed_total`
- `queueforge_runs_cancelled_total`
- `queueforge_runs_recovered_total`
- `queueforge_runs_duration_seconds`

## Recovery interpretation

| Error code | Meaning |
|---|---|
| `WORKER_EXIT_n` | Worker returned a non-zero exit |
| `WORKER_TIMEOUT` | Worker exceeded the configured deadline |
| `CONTROL_PLANE_RESTARTED` | API restarted during an active run |
| `CONTROL_PLANE_ERROR` | Unexpected orchestration failure |

Run `./VERIFY_PHASE_6.command` for the deterministic fault suite.
