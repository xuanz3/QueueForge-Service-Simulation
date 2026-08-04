# Reliability Model

QueueForge is a local-first control plane. Phase 6 hardens the boundaries that
are credible for that architecture rather than pretending it is a distributed
production platform.

## Failure boundaries

| Boundary | Protection | Evidence |
|---|---|---|
| API admission | Fixed maximum outstanding runs | Third request receives HTTP 429 |
| Worker process | Exit-code and stderr capture | Injected exit 23 becomes `WORKER_EXIT_23` |
| Worker duration | Hard process timeout and tree termination | Hanging worker becomes `WORKER_TIMEOUT` |
| User cancellation | Process-tree termination and terminal persistence | Active and queued runs become `CANCELLED` |
| API restart | Startup reconciliation of active rows | Interrupted run becomes `CONTROL_PLANE_RESTARTED` |
| Readiness | Database, worker executables and work-root checks | Actuator readiness group |
| Observability | Counters, active gauge and duration timer | Prometheus endpoint |

## Capacity policy

The admission controller owns a fair semaphore sized as:

```text
max concurrency + queue capacity
```

A request must acquire a permit before a database row is created. Exhausted
capacity returns HTTP 429 with `Retry-After: 2` and a structured capacity
snapshot.

Every accepted run releases exactly one permit after execution or terminal
short-circuiting.

## Non-goals

Phase 6 does not add distributed consensus, remote workers, message brokers or
automatic retry of non-idempotent work.
