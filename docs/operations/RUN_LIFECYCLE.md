# Run Lifecycle

## States

```text
QUEUED -> RUNNING -> SUCCEEDED
                   -> FAILED
                   -> CANCELLED
QUEUED ------------> CANCELLED
```

Terminal states never return to an active state.

## Submission

1. Spring validates the request.
2. A normalized request is serialized.
3. PostgreSQL creates a `QUEUED` record.
4. The bounded executor receives the run ID.
5. The API returns HTTP 202.

## Execution

1. The executor atomically claims `QUEUED` as `RUNNING`.
2. Java writes `request.json` into the run work directory.
3. Java starts the C++ or Python process with explicit arguments.
4. The process ID is persisted.
5. Java monitors timeout and cancellation.
6. Valid result JSON is persisted as `SUCCEEDED`.

## Failure

A failed run records a stable error code and a truncated human-readable message.

Examples:

- `WORKER_EXIT_65`
- `WORKER_TIMEOUT`
- `WORKER_RESULT_MISSING`
- `WORKER_IO`
- `CONTROL_PLANE_RESTARTED`

## Cancellation

Cancellation first sets `cancel_requested` in PostgreSQL, then terminates the active process and descendants. The final state is `CANCELLED`.

## Recovery

At startup, stale `QUEUED` and `RUNNING` rows become `FAILED`. QueueForge does not claim that an operating-system process survived without ownership.

## Evidence retention

Local work directories contain:

- normalized `request.json`
- `stdout.log`
- `stderr.log`
- worker-generated JSON and report files

The API result remains available from PostgreSQL after the container restarts.
