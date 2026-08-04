# Incident 005: Lifecycle Verifier Expected a Removed Declaration

## Summary

The V4 source correctly initialized `run_status` before its polling loop.
Repository verification failed before integration because an older V3
assertion still required the removed loop-local declaration.

The first recovery for this verifier issue also used an incorrectly escaped
exact-string search and therefore made no repository change.

## Root cause

Two verifier generations were active:

- the V3 fragment list required `    local run_status`
- the V4 structural rule rejected that same declaration inside the loop

The initial alignment script searched for the V3 line using two literal
backslashes when the Python source contained one escaped newline sequence.

## Resolution

The obsolete declaration entry is removed from the complete legacy fragment
block. The useful V3 checks remain:

- `run_status` assignment
- terminal-status `case`
- terminal-status output

The V4 structural checks remain:

- initialize `run_status` before the loop
- reject loop-local redeclaration

## Prevention

Verifier migrations should locate semantic blocks and validate retained rules,
rather than depend on one escaped source-code string.

## Impact

No Java, PostgreSQL, C++ or Python application source failed.
