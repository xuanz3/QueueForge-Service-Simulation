# Contributing

## Development flow

1. Create a focused branch from `main`.
2. Open or reference an Issue.
3. Keep commits scoped to one concern.
4. Add or update tests for behavioural changes.
5. Run the relevant phase verifier.
6. Run `./VERIFY_PHASE_8.command` before requesting final review.
7. Open a pull request with the checks performed and known limitations.

## Source expectations

- preserve versioned input and result contracts
- keep the C++ engine deterministic for fixed seeds
- do not bypass Java validation or PostgreSQL lifecycle persistence
- do not add generated runtime directories to Git
- document changes to reliability or performance budgets in an ADR
- retain exactly eight README screenshots unless a release deliberately changes
  the screenshot contract

## Commit examples

```text
feat(engine): add a queue discipline
fix(control-plane): preserve cancellation state
test(performance): add a regression workload
docs(release): clarify benchmark limitations
```
