# ADR-003: Use Explicit Random Transformations

- Status: Accepted
- Date: 2026-08-02

## Context

QueueForge must reproduce a simulation when the input, seed and engine version are unchanged.

The C++ standard random engines are deterministic, but standard probability-distribution implementations are not required to generate identical sequences across library implementations.

## Decision

QueueForge uses `std::mt19937_64` as the bit generator and implements:

- conversion from 53 random bits to a unit interval value
- exponential inter-arrival time by inverse transform
- triangular service time by inverse transform
- Bernoulli priority assignment by threshold comparison

## Consequences

Positive:

- the transformation is inspectable
- the same seed is less dependent on the standard library distribution implementation
- deterministic regression tests can compare complete result JSON

Negative:

- distribution code becomes part of the application responsibility
- numerical behaviour must be tested
- changing the algorithm requires an engine-version change

## Versioning rule

Any change that alters the generated event stream for an existing input and seed must change the engine version and include a migration note.
