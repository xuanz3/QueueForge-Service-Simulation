# README Screenshot Plan

The final README will contain eight images.

| Number | File | Evidence |
|---|---|---|
| 01 | `01-dashboard.webp` | Product overview and key metrics |
| 02 | `02-scenario-builder.webp` | Validated scenario configuration |
| 03 | `03-queue-timeline.webp` | Queue length over simulated time |
| 04 | `04-simulation-replay.webp` | Recorded event replay |
| 05 | `05-run-results.webp` | Single-run result detail |
| 06 | `06-staffing-comparison.webp` | Comparison across staff counts |
| 07 | `07-performance-benchmark.webp` | Measured C++ and Python evidence |
| 08 | `08-system-architecture.webp` | Component and data-flow architecture |

## Generation requirements

- Fixed browser viewport: 1440 × 900
- Fixed locale: English
- Fixed timezone: Australia/Melbourne
- Fixed demonstration scenario and seeds
- Disabled chart and CSS transitions
- Stable `data-testid` selectors
- API completion checks rather than arbitrary sleep delays
- WebP output
- Failure trace retained outside the README asset folder
- Automated verification that exactly eight files exist

Login screens, empty settings pages, duplicated charts and raw terminal screenshots will not consume the image budget.
