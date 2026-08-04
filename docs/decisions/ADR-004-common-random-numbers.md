# ADR-004: Use Common Random Numbers for Staffing Comparisons

- Status: Accepted
- Date: 2026-08-03

## Context

Independent random seed sets can make one staffing variant appear better or worse simply because it received easier or harder random arrivals.

QueueForge needs a comparison method that is easy to explain and reproduce.

## Decision

All staffing variants in one experiment use the same ordered seed schedule.

The C++ engine remains deterministic for each scenario, seed and engine version. Python changes only the server count while retaining the same seed for the corresponding run in every variant.

## Consequences

Positive:

- comparisons have lower avoidable random noise
- every run can be reproduced
- a failed or unusual seed can be inspected across all staffing variants
- the experiment does not require hidden global random state

Negative:

- observations across variants are paired rather than independent
- the current report does not yet calculate a paired confidence interval
- changing the seed schedule creates a different experiment version

## Future extension

Phase 7 may add paired delta intervals and bootstrap analysis. Phase 3 reports each variant independently and records the common-seed design explicitly.
