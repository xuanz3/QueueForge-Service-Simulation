# C++ Simulation Engine Design

## Purpose

The engine evaluates a bounded service scenario by processing timestamped events rather than advancing through fixed time steps.

## Supported events

1. `arrival`
2. `service_start`
3. `service_complete`

A service completion is processed before an arrival when both occur at the same timestamp. Remaining ties use a monotonically increasing sequence number. This makes event order explicit and repeatable.

## State

The engine maintains:

- a priority queue of scheduled events
- one customer record per arrival
- one mutable state record per server
- a FIFO or priority-FIFO waiting queue
- time-weighted queue length
- service-start waiting times
- an append-only event timeline

## Queue disciplines

### FIFO

All customers retain arrival order.

### Priority FIFO

Priority customers are selected before standard customers. Arrival order remains stable within each class.

Priority does not interrupt a service already in progress.

## Randomness

The engine uses `std::mt19937_64`, but does not use implementation-defined C++ distribution classes.

A 53-bit integer is mapped to `[0, 1)`. Exponential inter-arrival and triangular service durations are then calculated using explicit inverse-transform equations.

This narrows cross-platform variation and makes the algorithm inspectable.

## End-of-window behaviour

Events after the configured duration are not processed.

A customer can therefore be:

- completed
- waiting at the end
- still in service at the end

The required accounting identity is:

```text
arrived = completed + waiting_at_end + in_service_at_end
```

Server busy time is clipped to the simulation window.

## Metrics

Phase 2 reports:

- arrived and completed customers
- customers waiting or in service at the end
- average, median, P95 and maximum waiting time
- average and maximum queue length
- throughput per hour
- per-server and overall utilisation

P95 uses the nearest-rank definition.

## Deliberate limitations

Phase 2 does not include:

- abandonment
- staff breaks or shifts
- multiple service stages
- appointments
- time-varying arrival rates
- cost optimisation
- parallel execution

Those features are not required to validate the core event model.
