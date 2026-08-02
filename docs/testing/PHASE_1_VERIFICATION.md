# Phase 1 Verification

Phase 1 proves that the repository, container topology and all four language foundations build independently before simulation behaviour is added.

`VERIFY_PHASE_1.command` builds every image, runs each component's tests, verifies Java-to-PostgreSQL connectivity, checks the React server and executes the short-lived C++ and Python health commands.

This phase does not claim simulation, analytics or staffing functionality.
