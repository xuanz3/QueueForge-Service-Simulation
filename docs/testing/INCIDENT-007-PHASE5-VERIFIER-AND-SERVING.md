# Incident 007: Phase 5 Verifier and Web Serving Mismatch

## Summary

The three planned Phase 5 commits were created. Verification stopped before
TypeScript compilation because a repository assertion searched for a prose
fragment that did not exist in the source.

## Root cause

The service-time validation source contains concrete expressions:

```ts
minimumMinutes <= modeMinutes
modeMinutes <= maximumMinutes
```

The verifier instead searched for `minimum <= mode`.

A further review found that the Docker image built `dist` but started the Vite
development server. Runtime verification is intended to inspect the deployed
production JavaScript asset.

The TypeScript job also contained an unnecessary parent working-directory
override.

## Resolution

- verify concrete TypeScript comparison expressions
- add an explicit Vite production-preview script
- start the web container with `npm run preview`
- remove the redundant TypeScript-job source-check step
- add repository regression checks for all three conditions

## Impact

No Phase 5 feature source was discarded. The original three commits remain
intact and the recovery is recorded as one separate fix commit.
