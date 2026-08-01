# v1.0 Scope

## Included

- One service location
- One shared waiting queue
- Between 1 and 20 service staff
- Standard and priority customer classes
- FIFO and priority-FIFO queue disciplines
- Fixed, exponential and triangular service-time inputs
- Explicit random seeds
- Single simulation runs
- Repeated experiments across a fixed seed set
- Staffing comparison over a bounded range
- Waiting-time, queue-length, throughput and utilisation metrics
- Completed-run replay from recorded events
- Scenario version snapshots
- JSON, CSV and HTML result export
- PostgreSQL persistence
- Local Docker-based execution
- Automated README evidence generation

## Excluded from v1.0

- User registration and role-based access control
- Cloud hosting
- Kubernetes
- Kafka, RabbitMQ or other message brokers
- Real-time multi-user collaboration
- Live integration with an external queue system
- Machine-learning forecasts
- Natural-language recommendations
- Automatic staff rostering
- Multiple buildings or locations
- Arbitrary drag-and-drop process modelling
- Payment processing
- Mobile applications
- Real customer or employee data

## Scope-control rule

A feature can enter v1.0 only when it is required to complete the primary staffing-comparison workflow or to prove correctness, reproducibility, reliability or performance.

## Optional post-v1.0 extensions

- Customer abandonment
- Scheduled staff breaks
- Appointment and walk-in mixing
- Multi-stage service flows
- Multiple service locations
- Cost constraints and richer search strategies

Optional extensions must not delay the v1.0 release.
