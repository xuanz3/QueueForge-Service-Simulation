# User Stories

## Scenario definition

- As an operations analyst, I can create a named scenario so that its assumptions are reusable.
- As an operations analyst, I can configure arrival rate, service-time distribution, queue discipline and staff count.
- As an operations analyst, I receive clear validation errors before a simulation starts.

## Simulation

- As an operations analyst, I can provide an explicit random seed so that a run is reproducible.
- As an operations analyst, I can cancel a queued or running job.
- As an operations analyst, I can see whether a run is queued, simulating, analysing, completed, failed or cancelled.
- As an operations analyst, I can inspect a failure without reading raw internal stack traces.

## Results

- As an operations analyst, I can review average, median and P95 waiting time.
- As an operations analyst, I can review maximum queue length, throughput and staff utilisation.
- As an operations analyst, I can inspect the exact scenario snapshot used by an old run.
- As an operations analyst, I can replay a completed event timeline.

## Comparison

- As an operations analyst, I can compare a bounded set of staff counts using the same seed set.
- As an operations analyst, I can see uncertainty and sample size rather than only a single average.
- As an operations analyst, I can identify the lowest tested staff count that satisfies all declared objectives.
- As an operations analyst, I can see that a recommendation is limited to the tested range and assumptions.

## Audit and export

- As an operations analyst, I can export the scenario, seed set, software versions, metrics and limitations.
- As a reviewer, I can regenerate demonstration evidence from committed scripts and fixed data.
