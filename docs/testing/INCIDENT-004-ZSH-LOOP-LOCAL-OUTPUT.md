# Incident 004: Repeated zsh `local` Polluted Command Output

## Summary

The Java control plane started normally and completed an analytics run with
status `SUCCEEDED`. The verification script nevertheless entered its failure
branch and printed the successful run record.

## Root cause

`wait_for_terminal` declared `local run_status` inside its polling loop.

The first poll assigned `RUNNING`. On a later iteration the same local
parameter already existed. With the default zsh `TYPESET_SILENT` behaviour,
the `local`/`typeset` family may print an already-set parameter in assignment
form.

Because the entire function ran inside command substitution, that diagnostic
output was captured with the final `SUCCEEDED` value. The caller therefore did
not receive the exact string `SUCCEEDED`.

## Resolution

`run_status` is now initialized once before the loop:

```zsh
local run_status=""
for attempt in {1..180}; do
  run_status="..."
done
```

## Prevention

- repository verification checks that initialization precedes the loop
- repository verification rejects an indented loop-local redeclaration
- the lifecycle integration remains the publication gate

## Impact

The application and analytics worker were healthy. The failure was confined to
the shell verification result capture.
