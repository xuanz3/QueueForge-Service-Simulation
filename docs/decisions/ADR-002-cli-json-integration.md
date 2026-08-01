# ADR-002: Use Short-Lived CLI Workers and Versioned JSON

- Status: Accepted
- Date: 2026-08-01

## Context

Possible integration methods included JNI, Python native bindings, gRPC services and message queues.

## Decision

The Java control plane will invoke short-lived C++ and Python command-line workers. Input and output will use versioned JSON documents validated against committed schemas.

## Rationale

- simple local debugging
- deterministic artefact paths
- no internal network lifecycle
- direct process timeout and cancellation
- explicit exit codes
- inspectable evidence
- straightforward CI execution

## Rejected alternatives

### JNI or native bindings

They provide low call overhead but increase build, memory-safety and platform-debugging risk.

### Long-running gRPC workers

They provide a strong interface but introduce port, startup, health and shutdown concerns that are unnecessary for v1.0.

### Kafka or RabbitMQ

They would be disproportionate to a local single-user portfolio application.

## Consequences

- large payloads should use files rather than standard output
- schemas require compatibility tests
- Java must validate worker output before persistence
- process logs require correlation identifiers
