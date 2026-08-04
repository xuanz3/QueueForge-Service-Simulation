# Definition of Done

QueueForge v1.0 is complete only when all conditions below are met.

## Product

- A user can create a valid scenario.
- A user can run and cancel a simulation.
- A user can inspect a completed or failed run.
- A user can compare a bounded range of staff counts.
- A user can export JSON, CSV and HTML evidence.

## Correctness

- Equal input and seed produce equal deterministic engine output.
- Core simulation invariants are enforced by automated tests.
- The C++ implementation is cross-checked against a readable Python reference model.
- Scenario snapshots remain immutable after a run begins.
- Worker output is rejected when it fails contract validation.

## Reliability

- Missing workers, non-zero exits, timeouts, cancellation and malformed output have tested behaviour.
- At least one real defect follows Issue → fix → regression test → retest → postmortem.
- A Java process restart cannot silently convert an incomplete run into a successful run.

## Quality

- C++, Python, Java and web tests pass in CI.
- End-to-end tests cover scenario creation through report download.
- Linters and type checks run automatically.
- No secret, token or real personal record exists in the repository.

## Performance

- The benchmark method, machine, data size, versions and limitations are documented.
- At least one measured bottleneck is improved and retested.
- No unmeasured speedup claim appears in the README.

## Project

- README screenshot is generated from fixed demo data.
- No more than eight README images are used.
- Architecture decisions and known limitations are visible.
- A tagged v1.0 release can be rebuilt from a clean environment.
