# Java Control Plane Architecture

## Purpose

The Java control plane turns deterministic C++ and Python command-line workers into an auditable application service.

It owns:

- request validation
- run identity and lifecycle
- PostgreSQL persistence
- bounded local process execution
- timeout and cancellation
- result retrieval
- restart recovery

It does not reimplement simulation or statistics.

## Runtime components

The API image contains:

- Java 21 and Spring Boot 4.1
- Python 3.14 and the QueueForge analytics package
- the compiled C++20 simulation worker

The workers remain independent command-line programs. Java invokes them with explicit argument lists through `ProcessBuilder`; it does not construct shell commands.

## REST surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/runs` | Validate, persist and enqueue a simulation or analytics run |
| GET | `/api/runs` | List recent runs |
| GET | `/api/runs/{id}` | Read lifecycle metadata |
| GET | `/api/runs/{id}/result` | Read a successful JSON result |
| POST | `/api/runs/{id}/cancel` | Request cancellation |
| GET | `/api/system/status` | Check database, work directory and worker executables |

## Persistence boundary

PostgreSQL stores request and result JSON as evidence documents while lifecycle fields remain relational columns.

This preserves the versioned cross-language contracts without prematurely decomposing every result metric into database columns.

## Concurrency

A bounded two-thread executor limits local worker concurrency. Each run has a separate work directory and process ID.

The design avoids a message broker in v1 because:

- the project is local-first
- runs are bounded
- failures remain directly observable
- the operational cost stays at zero

## Restart behaviour

Queued or running database records cannot be assumed to still own a live process after a control-plane restart. Startup recovery therefore marks them failed with `CONTROL_PLANE_RESTARTED`.

Successful, failed and cancelled records remain available.
