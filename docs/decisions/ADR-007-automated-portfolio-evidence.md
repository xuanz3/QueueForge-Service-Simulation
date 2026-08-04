# ADR-007: Generate Portfolio Evidence from the Real Product

## Status

Accepted.

## Decision

The final README contains exactly eight PNG screenshots captured from the real
Docker product with Playwright. No screenshot may be a manually created
placeholder or a mock interface.

A temporary evidence configuration uses port `15177` and compiles the Web
bundle against `host.docker.internal:18086`. The normal local product is
restored to port `15176` after capture, including on failure.

## Evidence set

1. product overview
2. scenario configuration
3. live run lifecycle
4. staffing comparison
5. analytics JSON evidence
6. simulation KPI evidence
7. simulation JSON evidence
8. mobile interface

## Consequences

The screenshots can be reproduced from source, and the final release verifier
can enforce the image count, names, dimensions and README references.
