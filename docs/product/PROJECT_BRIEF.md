# Project Brief

## Product

QueueForge is a local-first service operations simulation and staffing analysis tool.

## Primary user

An operations analyst or service manager who needs to compare staffing configurations before altering a real service process.

## Demonstration organisation

The demonstration environment is a fictional **Melbourne Community Service Centre**. All people, workloads and operating data are generated for the project.

## Problem

Staffing decisions are often discussed using averages alone. Average demand can hide peak queues, long-tail waiting times and unstable utilisation. QueueForge provides a repeatable simulation workflow so a user can compare configurations under the same documented assumptions.

## Core workflow

1. Define a service scenario.
2. Select arrival and service-time assumptions.
3. Choose a queue discipline and staffing level.
4. Run a deterministic simulation using an explicit seed.
5. Review waiting time, queue length, throughput and utilisation.
6. Repeat the scenario over a fixed seed set.
7. Compare staffing options against stated service objectives.
8. Export an auditable report containing inputs, versions and limitations.

## Product value

QueueForge does not make an automatic workforce decision. It exposes the measured trade-off between service quality and staffing capacity within a declared search range.

## Engineering value

The project demonstrates that different languages can have clear responsibilities within one maintainable system:

- C++ for a compact, testable simulation engine
- Python for transparent statistical analysis
- Java for a durable application lifecycle
- TypeScript for an understandable product interface

## Success conditions

The project succeeds when a third party can reproduce a staffing comparison from a clean environment and trace every reported result to:

- a scenario snapshot
- a simulation seed set
- an engine and analytics version
- a committed input contract
- a recorded test environment
