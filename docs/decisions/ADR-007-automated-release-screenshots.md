# ADR-007: Capture Release Screenshots from the Running Product

## Status

Accepted.

## Decision

The README uses exactly eight PNG screenshots captured from the running Docker
product with Playwright. The screenshots are reproducible and cannot be replaced
with mock interfaces or manually assembled placeholders.

A temporary screenshot configuration uses port `15177` and compiles the Web
bundle against `host.docker.internal:18086`. The normal local product is
restored to port `15176` after capture, including when capture fails.

## Screenshot set

1. product overview
2. scenario configuration
3. live run lifecycle
4. staffing comparison
5. analytics JSON output
6. simulation KPI result
7. simulation JSON output
8. mobile interface

## Consequences

The release verifier checks names, count, dimensions, file sizes and README
references. JSON panels use tightly cropped element screenshots, while the
mobile view is displayed separately from desktop screenshots.
