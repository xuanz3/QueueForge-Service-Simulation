# Incident 012: Prometheus Verification Requested JSON

## Summary

All Phase 0–6 repository contracts passed, the Java test suite passed and the
API and React images built successfully. Runtime verification stopped when the
Prometheus endpoint returned HTTP 406.

## Observed failure

```text
AssertionError: 406
```

## Root cause

The shared Python HTTP helper defaults to:

```text
Accept: application/json
```

That is correct for QueueForge JSON APIs, but `/actuator/prometheus` produces
Prometheus text or OpenMetrics text. Spring correctly rejected the unsupported
JSON representation.

## Resolution

The Prometheus request now supplies an explicit metrics-text `Accept` header
covering:

- Prometheus text format 0.0.4
- OpenMetrics text format 1.0.0

All JSON API requests retain their existing JSON media type.

## Prevention

Phase 6 repository verification requires the explicit metrics media types and
rejects the previous JSON-default Prometheus call.

## Impact

No production endpoint or metric implementation failed. The issue was limited
to content negotiation in the verification client.
