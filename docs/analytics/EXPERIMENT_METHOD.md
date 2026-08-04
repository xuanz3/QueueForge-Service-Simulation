# Staffing Experiment Method

## Question

For the fictional service-centre scenario, which tested server count most consistently meets the committed demonstration target?

This is a software-engineering and statistical workflow demonstration. It is not operational staffing advice.

## Variants

The fixed evidence run compares:

- 3 servers
- 4 servers
- 5 servers

Each variant uses 40 runs.

## Common random numbers

Every variant uses the same seed schedule:

```text
20260801 through 20260840
```

Using the same seeds across variants reduces noise in comparisons because each staffing option is exposed to aligned random input streams.

## Target policy

A run meets the demonstration target when all conditions hold:

- run P95 waiting time is at most 10 minutes
- maximum queue length is at most 20
- overall utilisation is at most 85%

A staffing variant is eligible when at least 90% of its runs meet the target.

The selected variant is the lowest tested server count that is eligible and passes the analytical arrival-rate reasonableness check.

## Statistical output

For each run-level metric, the report includes:

- count
- mean
- sample standard deviation
- normal-approximation 95% confidence interval for the mean
- minimum
- median
- P95
- maximum

The confidence interval describes uncertainty in the run-level mean. It does not represent a guarantee for an individual customer.

## Analytical reference

The Python analytics layer calculates:

- expected Poisson arrival count
- triangular mean service time
- offered load in Erlangs
- nominal utilisation

The observed mean arrival count must fall within five standard errors of the Poisson expectation.

This is deliberately a broad reasonableness check. It does not replace simulation and is not presented as an exact queueing-theory oracle.

## Reproducibility

The report stores:

- complete scenario input
- seed range
- analytics version
- target policy
- every run-level result
- every variant summary
- limitations and the decision rule

Generated outputs are local evidence and are not committed as universal staffing claims.
