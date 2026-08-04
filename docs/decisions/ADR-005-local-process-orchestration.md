# ADR-005: Use Local Process Orchestration Before Messaging

- Status: Accepted
- Date: 2026-08-04

## Context

QueueForge needs Java lifecycle management around C++ simulation and Python analytics workers.

A message queue and separate worker deployment would add infrastructure, failure modes and cost before the workload requires them.

## Decision

Spring Boot uses `ProcessBuilder` to invoke versioned local CLI workers contained in the same application image.

Every command is represented as a list of arguments. No user-controlled value is interpolated into a shell command.

PostgreSQL remains the lifecycle source of truth.

## Controls

- bounded executor concurrency
- one work directory per run
- explicit process ID
- configurable timeout
- cancellation of child processes
- maximum request sizes enforced by validation
- output JSON parsed before success is persisted
- incomplete runs failed on application restart

## Consequences

Positive:

- local reproduction remains simple
- Java, C++ and Python boundaries are visible
- cancellation and stderr evidence are easy to inspect
- no broker or paid service is required

Negative:

- work is tied to one control-plane instance
- process state is not transferable between hosts
- horizontal scaling is intentionally unsupported

## Revisit condition

Introduce a durable queue only after measured workload or availability requirements exceed one bounded control-plane instance.
