# Contributing

QueueForge is a portfolio project, but changes should follow the same evidence
discipline as the original implementation.

## Development flow

1. Create a focused branch from `main`.
2. Open or reference an Issue.
3. Keep commits scoped to one concern.
4. Run the relevant phase verifier.
5. Run `./VERIFY_PHASE_8.command` before requesting final review.
6. Open a draft pull request with the verification evidence.

## Source expectations

- preserve versioned input and result contracts
- keep the C++ engine deterministic for fixed seeds
- do not bypass Java validation or PostgreSQL lifecycle persistence
- do not add generated runtime directories to Git
- do not weaken reliability or performance budgets without an ADR
- retain exactly eight README images unless a new release deliberately updates
  the final evidence contract

## Commit examples

```text
feat(engine): add a queue discipline
fix(control-plane): preserve cancellation state
test(performance): add a regression workload
docs(release): clarify benchmark limitations
```
