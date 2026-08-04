# Phase 3 Verification

## Unit tests

Python tests cover:

- nearest-rank quantiles
- run-level mean and confidence interval summaries
- analytical arrival and offered-load reference values
- lowest-eligible staffing selection
- JSON, CSV and HTML report generation

## Integration test

The analytics integration:

1. builds the C++20 engine
2. installs the Python analytics package
3. runs 40 common seeds for each of 3, 4 and 5 servers
4. captures 120 run-level results
5. verifies engine invariants for every run
6. checks observed mean arrivals against the analytical reference
7. verifies the committed demonstration decision rule
8. writes JSON, summary CSV, run-level CSV and HTML

## Fixed demonstration outcome

For engine version 0.2.0 and the committed basic scenario:

| Servers | Observed target success rate |
|---:|---:|
| 3 | 2.5% |
| 4 | 92.5% |
| 5 | 100.0% |

The decision rule therefore selects four servers as the lowest tested variant meeting the fictional 90% target.

This is a deterministic verification result for the committed seed schedule. It must not be presented as advice for a real service centre.

## Commands

```bash
./VERIFY_PHASE_3.command
```

Generated outputs:

```text
runtime/phase3/staffing-comparison.json
runtime/phase3/staffing-summary.csv
runtime/phase3/run-level-results.csv
runtime/phase3/staffing-report.html
```

## Known limitations

- only three server counts are tested
- the input rate is constant over the simulation window
- confidence intervals use a normal approximation
- no customer abandonment, shift schedule or service categories exist yet
- the target policy is illustrative
