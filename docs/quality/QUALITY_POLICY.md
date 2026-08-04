# Quality Policy

QueueForge treats quality as a set of reproducible gates rather than a claim
based on one successful demo.

## Source and repository gates

- generated runtime, build and coverage directories cannot be tracked
- dependency lock files are mandatory
- versioned JSON examples and budgets must parse
- operational scripts must retain their Git executable bit
- `git diff --check` must report no whitespace errors
- C++ release-quality verification runs in the API Docker build stage with warnings treated as errors

## Cross-language gates

| Component | Gate |
|---|---|
| C++ | Release build, tests, sanitizers and warning-free compilation |
| Python | Bytecode compilation, unit tests and analytics integration |
| Java | Maven tests and production-image build |
| React | TypeScript typecheck and Vite production build |
| Repository | Phase 0–7 contract verification |
| Runtime | Normal API, database, Web and worker lifecycle |

## Performance policy

Performance claims must include:

- scenario input
- run count and concurrency
- seed schedule
- Git commit
- platform and architecture
- measured percentiles
- budget values
- limitations

Budgets are guardrails against accidental regressions. They are deliberately
wide enough to run on common local laptops and GitHub-hosted runners. They are
not production service-level objectives.
