# QueueForge

QueueForge is a local-first service operations simulator for testing queue and
staffing decisions before they affect real operations. It combines a
deterministic C++20 simulation engine, Python multi-seed analytics, a Java
control plane, PostgreSQL persistence and a React interface.

## Product screenshots

<table>
<tr>
  <td width="50%"><img src="docs/assets/readme/01-product-overview.png" alt="Product overview and local stack status" width="100%"></td>
  <td width="50%"><img src="docs/assets/readme/02-scenario-configuration.png" alt="Scenario presets and operating assumptions" width="100%"></td>
</tr>
<tr>
  <td><sub>Product overview and local stack status</sub></td>
  <td><sub>Scenario presets and operating assumptions</sub></td>
</tr>
<tr>
  <td width="50%"><img src="docs/assets/readme/03-live-run-lifecycle.png" alt="Persisted live run lifecycle" width="100%"></td>
  <td width="50%"><img src="docs/assets/readme/04-staffing-comparison.png" alt="Multi-seed staffing comparison" width="100%"></td>
</tr>
<tr>
  <td><sub>Persisted live run lifecycle</sub></td>
  <td><sub>Multi-seed staffing comparison</sub></td>
</tr>
<tr>
  <td width="50%"><img src="docs/assets/readme/05-analytics-json-output.png" alt="Versioned analytics JSON output" width="100%"></td>
  <td width="50%"><img src="docs/assets/readme/06-simulation-kpis.png" alt="Deterministic simulation KPI result" width="100%"></td>
</tr>
<tr>
  <td><sub>Versioned analytics JSON output</sub></td>
  <td><sub>Deterministic simulation KPI result</sub></td>
</tr>
<tr>
  <td colspan="2">
    <img src="docs/assets/readme/07-simulation-json-output.png" alt="Versioned simulation JSON output" width="100%">
  </td>
</tr>
<tr>
  <td colspan="2"><sub>Versioned simulation JSON output</sub></td>
</tr>
</table>

<p align="center">
  <img src="docs/assets/readme/08-mobile-interface.png" alt="Responsive mobile interface" width="320">
  <br>
  <sub>Responsive mobile interface</sub>
</p>

## System capabilities

- validates and reproduces versioned queue scenarios
- produces deterministic C++ results for fixed seeds
- compares staffing options across repeated Python simulations
- persists and supervises worker execution through Spring Boot
- retains lifecycle, errors and results across PostgreSQL-backed restarts
- returns structured HTTP 429 responses under capacity pressure
- handles worker failure, timeout, cancellation and control-plane restart
- connects the React interface to the real API rather than mock data

## Architecture

| Component | Responsibility |
|---|---|
| React + TypeScript | Scenario configuration, run tracking and result review |
| Java + Spring Boot | Validation, bounded admission, lifecycle and process control |
| PostgreSQL + Flyway | Durable request, status, error and result persistence |
| Python | Multi-seed experiments, statistics and staffing comparison |
| C++20 | Deterministic discrete-event queue simulation |
| Docker Compose | Reproducible local product and verification environment |
| GitHub Actions | Cross-language build, integration, reliability and performance checks |

## Reference measurements

The values below were recorded by `./VERIFY_PHASE_7.command` through the normal
Docker product stack. They are regression measurements from one documented
environment, not production service-level objectives.

| Check | Measured result |
|---|---:|
| C++ deterministic output | PASS |
| C++ p95 execution | 1.901 ms |
| Python staffing analysis | 0.586 s |
| API simulation success | 100% |
| API submit p95 | 81.8 ms |
| API end-to-end p95 | 199.79 ms |
| Production JavaScript | 207,944 bytes |
| Production CSS | 9,018 bytes |
| API image | 150,540,420 bytes |
| Web image | 21,891,910 bytes |

## Run locally

Requirements:

- Docker Desktop
- Git
- Python 3
- zsh on macOS/Linux

Start and verify the complete product:

```bash
./VERIFY_PHASE_8.command
```

Open:

```text
http://localhost:15176
```

Docker provides the C++, Java, Node, PostgreSQL and browser toolchains, so they
do not need to be installed directly on the host.

## Documentation

- [System architecture](docs/architecture/CONTROL_PLANE.md)
- [Reliability model](docs/architecture/RELIABILITY_MODEL.md)
- [Quality policy](docs/quality/QUALITY_POLICY.md)
- [Performance method](docs/performance/PERFORMANCE_METHOD.md)
- [Run lifecycle](docs/operations/RUN_LIFECYCLE.md)
- [Reliability playbook](docs/operations/RELIABILITY_PLAYBOOK.md)
- [Project summary](docs/release/PROJECT_SUMMARY.md)
- [v1.0.0 release notes](docs/release/RELEASE_NOTES_v1.0.0.md)
- [Release verification](docs/testing/PHASE_8_VERIFICATION.md)

## Delivery history

1. Product definition
2. Repository and local environment
3. C++ simulation engine
4. Python analytics
5. Java control plane
6. React product interface
7. Reliability and fault handling
8. Quality and performance
9. Production release

All planned phases are complete in `v1.0.0`.

## Scope and limitations

QueueForge is a local reference implementation. It does not claim distributed
worker coordination, cloud-scale capacity or operational staffing advice.
Performance values depend on the recorded host, Docker version and workload.

## License

MIT. See [LICENSE](LICENSE).
