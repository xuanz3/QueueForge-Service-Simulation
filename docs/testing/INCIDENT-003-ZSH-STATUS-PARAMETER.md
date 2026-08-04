# Incident 003: zsh Read-Only `status` Parameter

## Summary

After the Spring constructor fix, the API image rebuilt, PostgreSQL was healthy
and the API container started. The Phase 4 lifecycle script then stopped before
it could observe the first run reaching a terminal state.

## Observed failure

```text
wait_for_terminal: read-only variable: status
```

## Root cause

`RUN_CONTROL_PLANE_DEMO.command` uses zsh.

In zsh, `status` is a special read-only parameter that exposes the previous
command's exit status. The `wait_for_terminal` function attempted to declare and
assign a local variable with that reserved name.

## Resolution

The lifecycle response field is now stored in `run_status`.

## Prevention

- repository verification rejects `local status`
- repository verification requires the `run_status` declaration and case check
- the complete lifecycle command remains the final integration gate
- the branch is not published until the gate passes

## Impact

The Java application itself did not fail at this point. The failure was isolated
to the local verification shell script.
