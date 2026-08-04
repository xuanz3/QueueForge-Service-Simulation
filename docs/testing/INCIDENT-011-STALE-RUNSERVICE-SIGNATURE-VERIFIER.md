# Incident 011: RunService Signature Verifier Became Stale

## Summary

The three planned Phase 6 commits were created. Repository verification stopped
before compilation because the inherited Phase 4 verifier required one exact
historical `RunService` constructor signature.

## Observed failure

```text
RunService production constructor is not explicitly autowired
```

## Root cause

The Phase 6 constructor remained explicitly annotated with `@Autowired`, but it
correctly gained two dependencies:

- `RunAdmissionController`
- `RunTelemetry`

The verifier compared the full source against the old five-argument signature,
so any legitimate constructor extension appeared to remove the annotation.

## Resolution

The verifier now checks separately that:

1. `@Autowired` immediately precedes the public production constructor.
2. The original Phase 4 dependencies remain present.
3. The Phase 6 admission and telemetry dependencies are present.
4. The Spring application-context regression test remains mandatory.

## Prevention

Future phases may extend the constructor without rewriting a historical exact
signature, while still being required to preserve explicit injection and all
core dependencies.

## Impact

No Java implementation defect was found. The failure was isolated to a stale
repository assertion.
