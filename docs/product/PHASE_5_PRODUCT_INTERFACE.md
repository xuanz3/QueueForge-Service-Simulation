# Phase 5 Product Interface

## Purpose

Phase 5 turns QueueForge from a collection of verified services into an
operator-facing workflow.

The interface is not a mock dashboard. It submits the same versioned requests
used by the Java control plane and presents persisted lifecycle state and worker
results.

## User workflow

1. Confirm that the local Java, PostgreSQL, Python and C++ stack is ready.
2. Choose a committed scenario preset or edit the assumptions.
3. Select a single deterministic simulation or a multi-seed staffing analysis.
4. Validate client-side constraints that mirror the Java contract.
5. Submit the run and observe QUEUED, RUNNING and terminal state.
6. Cancel a long-running analysis when required.
7. Review simulation metrics or compare staffing variants.
8. Inspect the complete versioned JSON output.

## Interface principles

- operational rather than decorative
- one primary workflow per screen
- explicit fictional-data boundary
- accessible labels and native controls
- responsive layout without a component framework
- no hard-coded successful result
- no browser persistence of sensitive or operational data

## Scope boundary

Phase 5 does not add authentication, distributed execution, saved scenario
libraries or production staffing advice. Reliability hardening belongs to
Phase 6.
