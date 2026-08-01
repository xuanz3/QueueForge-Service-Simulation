# Metrics and Assumptions

## Decision metrics

QueueForge will report:

- Arrived customers
- Completed customers
- Customers waiting at the end
- Customers still in service at the end
- Average waiting time
- Median waiting time
- P95 waiting time
- Maximum waiting time
- Average queue length
- Maximum queue length
- Throughput
- Per-server utilisation
- Overall utilisation
- Simulation execution time

## Demonstration service objectives

The demonstration scenario may use the following objectives:

- Average waiting time at or below 5 minutes
- P95 waiting time at or below 12 minutes
- Overall utilisation at or below 85%

These are fictional demonstration objectives. They are not presented as standards for healthcare, government or commercial services.

## Recommendation language

The product must not state that a configuration is globally optimal.

Permitted wording:

> Within the tested staff range, scenario assumptions and seed set, this is the lowest staff count that met every declared objective.

## Statistical reporting

Repeated experiments must report:

- Number of seeds
- Exact seed-generation method or committed seed list
- Mean or median as appropriate
- P95 where relevant
- A confidence interval for selected aggregate metrics
- Missing or failed runs
- Software version
- Test environment

## Simulation invariants

For runs without abandonment:

```text
arrived = completed + waiting_at_end + in_service_at_end
```

For every customer:

```text
service_start_time >= arrival_time
service_complete_time >= service_start_time
```

For every server:

```text
0 <= utilisation <= 1
```

## Initial modelling assumptions

- Simulation time is measured in minutes.
- A shared queue feeds all available servers.
- A server handles at most one customer at a time.
- Events occurring at the same timestamp use a documented deterministic tie-break order.
- The v1.0 model uses one local timezone and does not model daylight-saving transitions.
- Generated demo data contains no real personal information.
