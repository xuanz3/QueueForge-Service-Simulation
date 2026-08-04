# Phase 7 Verification

Run:

```bash
./VERIFY_PHASE_7.command
```

## Quality matrix

| Area | Verification |
|---|---|
| Repository | Generated data excluded, lock files present, executable bits retained |
| C++ | Dockerized GCC/CMake release build with `-Werror` and complete CTest suite |
| Python | Bytecode compilation and unit tests |
| Java | Maven test/package Docker stage |
| React | Dedicated TypeScript typecheck Docker target |
| Runtime | Normal PostgreSQL, API and Web stack |
| Performance | Ten portable regression budgets |

## Performance gates

- fixed-seed C++ output remains deterministic
- C++ p95 stays below the portable latency budget
- Python staffing analysis stays below its wall-time budget
- concurrent API simulations complete successfully
- API submit and end-to-end p95 remain within budget
- production JavaScript and CSS remain within size budgets
- API and Web images remain within size budgets

## Generated evidence

```text
runtime/phase7/performance-report.json
runtime/phase7/performance-report.md
runtime/phase7/staffing-comparison.json
```

GitHub Actions uploads the directory as `phase7-performance-evidence`.

The budgets are regression guardrails, not production service-level
objectives.
