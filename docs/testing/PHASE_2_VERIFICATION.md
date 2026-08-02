# Phase 2 Verification

## Automated C++ tests

The engine has separate tests for:

- JSON parsing, escaping and duplicate-key rejection
- FIFO and priority-FIFO ordering
- input and output mapping
- deterministic repeated simulations
- accounting, chronology and utilisation invariants
- invalid service-distribution rejection
- engine health output

## Local verification

Run:

```bash
./VERIFY_PHASE_2.command
```

The command:

1. verifies repository files and contracts
2. verifies the C++ runtime compatibility controls
3. builds the final C++ Docker image
4. runs the basic scenario twice
5. compares both result files byte for byte
6. runs an overloaded scenario
7. checks output invariants
8. validates a contract without simulation
9. confirms invalid input exits with code 65

## CI verification

GitHub Actions runs:

- release compilation and CTest
- AddressSanitizer and UndefinedBehaviorSanitizer tests
- example input validation
- repository and Compose checks
- unchanged Java, Python and web foundation checks

## Reference result

The committed repository does not store a claimed staffing result.

The fixed demonstration scenario is generated during verification. Its metrics are valid only for the committed assumptions, seed and engine version.

## Known limits

- A single seed is not enough for a staffing decision.
- Phase 3 will run repeated seeds and report uncertainty.
- The internal JSON codec intentionally supports standard JSON, but it is not presented as a general-purpose replacement for a mature JSON library.
