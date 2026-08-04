from __future__ import annotations

import datetime as dt
import json
import platform
import re
import struct
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCREEN_DIR = ROOT / "docs/assets/readme"
PERFORMANCE_REPORT = ROOT / "runtime/phase7/performance-report.json"
RELIABILITY_REPORT = ROOT / "runtime/phase6/reliability-evidence.json"
RELEASE_DIR = ROOT / "docs/release"
RELEASE_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS = [
    ("01-product-overview.png", "Product overview and local stack status"),
    ("02-scenario-configuration.png", "Scenario presets and operating assumptions"),
    ("03-live-run-lifecycle.png", "Persisted live run lifecycle"),
    ("04-staffing-comparison.png", "Multi-seed staffing comparison"),
    ("05-analytics-json-output.png", "Versioned analytics JSON output"),
    ("06-simulation-kpis.png", "Deterministic simulation KPI result"),
    ("07-simulation-json-output.png", "Versioned simulation JSON output"),
    ("08-mobile-interface.png", "Responsive mobile interface"),
]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"Not a PNG file: {path}")
    return struct.unpack(">II", data[16:24])


def number(value: Any, digits: int = 3) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value:,.{digits}f}".rstrip("0").rstrip(".")
    return str(value)


if not PERFORMANCE_REPORT.is_file():
    raise SystemExit("Phase 7 performance report is missing.")

performance = json.loads(PERFORMANCE_REPORT.read_text(encoding="utf-8"))
reliability_report_present = RELIABILITY_REPORT.is_file()

files = sorted(path.name for path in SCREEN_DIR.glob("*.png"))
expected = [name for name, _ in SCREENSHOTS]
if files != expected:
    raise SystemExit(
        "Screenshot set is not exact:\n"
        f"expected={expected}\nactual={files}"
    )

screenshot_manifest = []
for name, description in SCREENSHOTS:
    path = SCREEN_DIR / name
    width, height = png_dimensions(path)
    screenshot_manifest.append(
        {
            "file": f"docs/assets/readme/{name}",
            "description": description,
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
        }
    )

measurements = performance["measurements"]
cpp = measurements["cpp"]
analytics = measurements["analytics"]
api = measurements["api"]
web = measurements["web"]
images = measurements["images"]

paired_rows = []
for index in range(0, 6, 2):
    left_name, left_alt = SCREENSHOTS[index]
    right_name, right_alt = SCREENSHOTS[index + 1]
    paired_rows.append(
        "<tr>\n"
        f'  <td width="50%"><img src="docs/assets/readme/{left_name}" '
        f'alt="{left_alt}" width="100%"></td>\n'
        f'  <td width="50%"><img src="docs/assets/readme/{right_name}" '
        f'alt="{right_alt}" width="100%"></td>\n'
        "</tr>\n"
        "<tr>\n"
        f"  <td><sub>{left_alt}</sub></td>\n"
        f"  <td><sub>{right_alt}</sub></td>\n"
        "</tr>"
    )

desktop_output_name, desktop_output_alt = SCREENSHOTS[6]
mobile_name, mobile_alt = SCREENSHOTS[7]
gallery = "\n".join(paired_rows)

readme = f"""# QueueForge

QueueForge is a local-first service operations simulator for testing queue and
staffing decisions before they affect real operations. It combines a
deterministic C++20 simulation engine, Python multi-seed analytics, a Java
control plane, PostgreSQL persistence and a React interface.

## Product screenshots

<table>
{gallery}
<tr>
  <td colspan="2">
    <img src="docs/assets/readme/{desktop_output_name}" alt="{desktop_output_alt}" width="100%">
  </td>
</tr>
<tr>
  <td colspan="2"><sub>{desktop_output_alt}</sub></td>
</tr>
</table>

<p align="center">
  <img src="docs/assets/readme/{mobile_name}" alt="{mobile_alt}" width="320">
  <br>
  <sub>{mobile_alt}</sub>
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
| C++ deterministic output | {"PASS" if cpp["deterministic"] else "FAIL"} |
| C++ p95 execution | {number(cpp["p95Milliseconds"])} ms |
| Python staffing analysis | {number(analytics["elapsedSeconds"])} s |
| API simulation success | {number(api["successRate"] * 100, 1)}% |
| API submit p95 | {number(api["submitP95Milliseconds"])} ms |
| API end-to-end p95 | {number(api["endToEndP95Milliseconds"])} ms |
| Production JavaScript | {web["javascriptBytes"]:,} bytes |
| Production CSS | {web["cssBytes"]:,} bytes |
| API image | {images["apiBytes"]:,} bytes |
| Web image | {images["webBytes"]:,} bytes |

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
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")

summary = f"""# QueueForge Project Summary

## Purpose

QueueForge tests queue and staffing decisions through a reproducible local
simulation workflow. Users can run one deterministic scenario or compare
staffing options across repeated seeds, then inspect the persisted lifecycle and
versioned JSON output.

## Engineering scope

- C++20 discrete-event simulation
- Python experiment orchestration and statistics
- Java 21 / Spring Boot REST control plane
- PostgreSQL persistence and Flyway migration
- React and TypeScript product interface
- Docker multi-stage builds and Compose integration
- GitHub Actions for unit, integration, reliability and performance checks
- Micrometer, Actuator and Prometheus telemetry
- Playwright screenshot automation

## Reference results

- deterministic C++ output: {"pass" if cpp["deterministic"] else "fail"}
- C++ p95: {number(cpp["p95Milliseconds"])} ms
- Python analytics: {number(analytics["elapsedSeconds"])} s
- API success rate: {number(api["successRate"] * 100, 1)}%
- API end-to-end p95: {number(api["endToEndP95Milliseconds"])} ms
- README screenshots: 8

## Reliability checks

The automated suite covers bounded admission, HTTP 429 responses, worker exit,
worker timeout, API restart reconciliation and restoration of a successful
normal simulation.

## Operating boundary

QueueForge is intended for local evaluation with fictional scenarios. It is not
a distributed job platform or an operational staffing recommendation system.
"""
(RELEASE_DIR / "PROJECT_SUMMARY.md").write_text(summary, encoding="utf-8")

release_notes = f"""# QueueForge v1.0.0

QueueForge v1.0.0 is the first stable release of the local-first service
operations simulator.

## Included

- deterministic C++20 queue simulation
- Python multi-seed staffing analytics
- Java / Spring Boot run control plane
- PostgreSQL persistence and Flyway migration
- React / TypeScript product interface
- bounded admission, cancellation, timeout and restart recovery
- Actuator and Prometheus telemetry
- cross-language quality and performance budgets
- automated eight-image product screenshot capture

## Verification highlights

- all Phase 0–8 repository contracts
- C++ release, sanitizers and warnings-as-errors
- Python package and integration tests
- Java tests and full process lifecycle
- React production build and real API integration
- capacity, worker failure, timeout and restart fault injection
- ten performance regression checks
- exact eight-image README screenshot contract

## Reference environment

- platform: {performance["environment"]["platform"]}
- architecture: {performance["environment"]["architecture"]}
- Docker server: {performance["environment"]["dockerServer"]}
- performance revision: `{performance["environment"]["gitCommit"]}`

## Limitations

Reference measurements are regression checks from one documented environment,
not a production SLO or a staffing recommendation.
"""
(RELEASE_DIR / "RELEASE_NOTES_v1.0.0.md").write_text(
    release_notes,
    encoding="utf-8",
)

manifest = {
    "schemaVersion": "1.0",
    "release": "v1.0.0",
    "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
    "documentationRevision": git("rev-parse", "HEAD"),
    "platform": platform.platform(),
    "performancePassed": performance.get("passed") is True,
    "performanceChecks": performance.get("gates", []),
    "reliabilityReportPresent": reliability_report_present,
    "readmeScreenshotCount": len(screenshot_manifest),
    "screenshots": screenshot_manifest,
}
(RELEASE_DIR / "RELEASE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2) + "\n",
    encoding="utf-8",
)

image_references = re.findall(
    r'<img\s+[^>]*src="docs/assets/readme/[^"]+\.png"',
    readme,
)
if len(image_references) != 8:
    raise SystemExit(
        f"Generated README contains {len(image_references)} image references."
    )

print("Generated README, project summary, release notes and manifest.")
