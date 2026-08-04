# ADR-001: Use a Polyglot Architecture with Explicit Responsibilities

- Status: Accepted
- Date: 2026-08-01

## Context

The project objective requires credible Java, Python and C++ evidence. Creating unrelated demonstrations would not show how the languages cooperate in a maintainable product.

## Decision

QueueForge will use:

- C++20 for the deterministic discrete-event engine
- Python for repeated experiments and statistical reporting
- Java / Spring Boot for validation, orchestration, persistence and lifecycle handling
- React / TypeScript for the product interface

Every component must have tests that can run independently.

## Alternatives considered

### Implement everything in Java

This would reduce integration work but would not provide meaningful Python or C++ engineering criteria.

### Implement independent projects per language

This would be easier to organise but would weaken the product narrative and duplicate setup work.

### Use Python for the entire simulation stack

This would be suitable for experimentation but would not demonstrate native performance engineering and modern C++ practices.

## Consequences

Positive:

- each language has a defensible responsibility
- cross-language contracts become visible engineering criteria
- performance and reference implementations can be compared

Negative:

- contracts require deliberate versioning
- process failures must be handled
- the local toolchain is broader

The project accepts these costs but avoids unnecessary distributed infrastructure.
