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
PERFORMANCE = ROOT / "runtime/phase7/performance-report.json"
RELIABILITY = ROOT / "runtime/phase6/reliability-evidence.json"
RELEASE_DIR = ROOT / "docs/release"
RELEASE_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS = [
    ("01-product-overview.png", "Product overview and local stack status"),
    ("02-scenario-configuration.png", "Scenario presets and operating assumptions"),
    ("03-live-run-lifecycle.png", "Persisted live run lifecycle"),
    ("04-staffing-comparison.png", "Multi-seed staffing comparison"),
    ("05-analytics-json-evidence.png", "Versioned analytics JSON evidence"),
    ("06-simulation-kpis.png", "Deterministic simulation KPI result"),
    ("07-simulation-json-evidence.png", "Versioned simulation JSON evidence"),
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
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def number(value: Any, digits: int = 3) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value:,.{digits}f}".rstrip("0").rstrip(".")
    return str(value)


if not PERFORMANCE.is_file():
    raise SystemExit("Phase 7 performance report is missing.")
performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))

reliability = {}
if RELIABILITY.is_file():
    reliability = json.loads(RELIABILITY.read_text(encoding="utf-8"))

files = sorted(path.name for path in SCREEN_DIR.glob("*.png"))
expected = [name for name, _ in SCREENSHOTS]
if files != expected:
    raise SystemExit(
        "Screenshot set is not exact:\n"
        f"expected={expected}\nactual={files}"
    )

image_manifest = []
for name, description in SCREENSHOTS:
    path = SCREEN_DIR / name
    width, height = png_dimensions(path)
    if width < 390 or height < 700:
        raise SystemExit(f"Screenshot dimensions are too small: {name}")
    image_manifest.append(
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

gallery_rows = []
for index in range(0, len(SCREENSHOTS), 2):
    left_name, left_alt = SCREENSHOTS[index]
    right_name, right_alt = SCREENSHOTS[index + 1]
    gallery_rows.append(
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
gallery = "\n".join(gallery_rows)

readme = f"""# QueueForge

QueueForge is a local-first service operations simulator for testing queue and
staffing decisions before they affect real operations. It combines a
deterministic C++20 simulation engine, Python multi-seed analytics, a Java
control plane, PostgreSQL persistence and a React interface.

## Product evidence

<table>
{gallery}
</table>

## What the system proves

- versioned queue scenarios can be validated and reproduced
- fixed seeds produce deterministic C++ results
- Python can compare staffing options across repeated simulations
- Java persists and supervises worker execution
- PostgreSQL retains lifecycle and result evidence across restarts
- bounded admission returns explicit HTTP 429 responses under saturation
- worker failure, timeout, cancellation and control-plane restart are recoverable
- the React product interface uses the real API rather than mock data

## Architecture

| Component | Responsibility |
|---|---|
| React + TypeScript | Scenario configuration, run tracking and evidence review |
| Java + Spring Boot | Validation, bounded admission, lifecycle and process control |
| PostgreSQL + Flyway | Durable request, status, error and result persistence |
| Python | Multi-seed experiments, statistics and staffing recommendation |
| C++20 | Deterministic discrete-event queue simulation |
| Docker Compose | Reproducible local product and verification environment |
| GitHub Actions | Cross-language build, integration, reliability and performance gates |

## Reference verification

The values below were generated by `./VERIFY_PHASE_7.command` through the
normal Docker product stack. They are regression evidence from the recorded
environment, not production service-level objectives.

| Gate | Measured result |
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

The verification commands deliberately use Docker for C++, Java, Node,
PostgreSQL and browser evidence so the host machine does not require those
toolchains directly.

## Evidence and documentation

- [System architecture](docs/architecture/CONTROL_PLANE.md)
- [Reliability model](docs/architecture/RELIABILITY_MODEL.md)
- [Quality policy](docs/quality/QUALITY_POLICY.md)
- [Performance method](docs/performance/PERFORMANCE_METHOD.md)
- [Run lifecycle](docs/operations/RUN_LIFECYCLE.md)
- [Reliability playbook](docs/operations/RELIABILITY_PLAYBOOK.md)
- [Release summary](docs/release/PORTFOLIO_SUMMARY.md)
- [v1.0.0 release notes](docs/release/RELEASE_NOTES_v1.0.0.md)
- [Final verification contract](docs/testing/PHASE_8_VERIFICATION.md)

## Delivery history

1. Product definition
2. Repository and local environment
3. C++ simulation engine
4. Python analytics
5. Java control plane
6. React product interface
7. Reliability and fault handling
8. Quality and performance
9. Final portfolio release

All phases are complete in `v1.0.0`.

## Scope and limitations

QueueForge is a portfolio-grade local product. It does not claim distributed
worker coordination, cloud-scale capacity or operational staffing advice.
Performance values depend on the recorded host, Docker version and workload.

## License

MIT. See [LICENSE](LICENSE).
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")

summary = f"""# QueueForge Portfolio Summary

## Product

QueueForge is a complete local-first service operations simulator. A user can
configure a queue scenario, execute one deterministic simulation or compare
staffing options across repeated runs, observe the durable lifecycle and inspect
versioned JSON evidence.

## Engineering coverage

- C++20 discrete-event simulation
- Python experiment orchestration and statistics
- Java 21 / Spring Boot REST control plane
- PostgreSQL persistence and Flyway migration
- React and TypeScript product interface
- Docker multi-stage builds and Compose integration
- GitHub Actions across unit, integration, reliability and performance gates
- Micrometer, Actuator and Prometheus telemetry
- Playwright evidence automation

## Verified reference results

- deterministic C++ output: {"pass" if cpp["deterministic"] else "fail"}
- C++ p95: {number(cpp["p95Milliseconds"])} ms
- Python analytics: {number(analytics["elapsedSeconds"])} s
- API success rate: {number(api["successRate"] * 100, 1)}%
- API end-to-end p95: {number(api["endToEndP95Milliseconds"])} ms
- final README screenshots: 8

## Reliability evidence

The automated suite verifies bounded admission, HTTP 429, worker exit,
worker timeout, API restart reconciliation and restoration of a successful
normal simulation.

## Review path

A reviewer can understand the project in this order:

1. README product evidence
2. architecture responsibilities
3. reliability model
4. quality and performance method
5. phase-based PR and Issue history
6. v1.0.0 release
"""

(RELEASE_DIR / "PORTFOLIO_SUMMARY.md").write_text(summary, encoding="utf-8")

release_notes = f"""# QueueForge v1.0.0

QueueForge v1.0.0 is the first complete portfolio release of the local-first
service operations simulator.

## Included

- deterministic C++20 queue simulation
- Python multi-seed staffing analytics
- Java / Spring Boot run control plane
- PostgreSQL persistence and Flyway migration
- React / TypeScript product interface
- bounded admission, cancellation, timeout and restart recovery
- Actuator and Prometheus telemetry
- cross-language quality and performance budgets
- automated eight-image portfolio evidence

## Verification highlights

- all Phase 0–8 repository contracts
- C++ release, sanitizers and warnings-as-errors
- Python package and integration tests
- Java tests and full process lifecycle
- React production build and real API integration
- capacity, worker failure, timeout and restart fault injection
- ten performance regression gates
- exact eight-image README evidence contract

## Reference environment

- platform: {performance["environment"]["platform"]}
- architecture: {performance["environment"]["architecture"]}
- Docker server: {performance["environment"]["dockerServer"]}
- performance commit: `{performance["environment"]["gitCommit"]}`

## Limitations

Reference measurements are portable regression evidence, not a production SLO
or a staffing recommendation.
"""
(RELEASE_DIR / "RELEASE_NOTES_v1.0.0.md").write_text(
    release_notes,
    encoding="utf-8",
)

manifest = {
    "schemaVersion": "1.0",
    "release": "v1.0.0",
    "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
    "branch": git("branch", "--show-current"),
    "sourceCommit": git("rev-parse", "HEAD"),
    "platform": platform.platform(),
    "performancePassed": performance.get("passed") is True,
    "performanceGates": performance.get("gates", []),
    "reliabilityEvidencePresent": bool(reliability),
    "readmeImageCount": len(image_manifest),
    "images": image_manifest,
}
(RELEASE_DIR / "RELEASE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2),
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

print("Generated final README, release notes, summary and manifest.")
