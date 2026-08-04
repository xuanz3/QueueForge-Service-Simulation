from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import math
import os
import platform
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "runtime" / "phase7"
RUNTIME.mkdir(parents=True, exist_ok=True)

API = "http://localhost:18086"
WEB = "http://localhost:15176"
SCENARIO = ROOT / "contracts/examples/basic-scenario.json"
BUDGETS_PATH = ROOT / "performance/phase7-budgets.json"

FAULT_KEYS = {
    "QUEUEFORGE_SIMULATION_COMMAND",
    "QUEUEFORGE_WORKER_TIMEOUT",
    "QUEUEFORGE_WORKER_CONCURRENCY",
    "QUEUEFORGE_WORKER_QUEUE_CAPACITY",
    "QUEUEFORGE_FAULT_DELAY_SECONDS",
}


def normal_environment() -> dict[str, str]:
    result = os.environ.copy()
    for key in FAULT_KEYS:
        result.pop(key, None)
    return result


ENV = normal_environment()


def run(
    args: list[str],
    *,
    input_text: str | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        env=ENV,
        input=input_text,
        text=True,
        capture_output=capture,
        check=True,
    )


def compose(*args: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", *args], capture=capture)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("Cannot calculate a percentile from no values")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def request(
    url: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    timeout: float = 20,
) -> tuple[int, dict[str, str], bytes]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def json_request(
    path: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    expected: set[int] = {200},
) -> tuple[int, dict[str, str], dict[str, Any]]:
    status, headers, body = request(
        API + path,
        method=method,
        payload=payload,
    )
    if status not in expected:
        raise RuntimeError(
            f"{method} {path} returned {status}: {body.decode(errors='replace')}"
        )
    parsed = json.loads(body) if body else {}
    if not isinstance(parsed, dict):
        raise RuntimeError(f"{path} did not return a JSON object")
    return status, headers, parsed


def wait_ready(attempts: int = 120) -> dict[str, Any]:
    last: Exception | None = None
    for _ in range(attempts):
        try:
            _, _, body = json_request(
                "/actuator/health/readiness",
                expected={200},
            )
            if body.get("status") == "UP":
                return body
        except Exception as error:
            last = error
        time.sleep(1)
    raise RuntimeError("QueueForge API did not become ready") from last


def git_output(*args: str) -> str:
    return run(["git", *args], capture=True).stdout.strip()


def docker_output(*args: str) -> str:
    return run(["docker", *args], capture=True).stdout.strip()


def copy_scenario_to_api() -> str:
    container_id = compose("ps", "-q", "api", capture=True).stdout.strip()
    if not container_id:
        raise RuntimeError("The API container is not running")
    target = "/tmp/queueforge-phase7-scenario.json"
    run(["docker", "cp", str(SCENARIO), f"{container_id}:{target}"])
    return target


def benchmark_cpp(iterations: int, scenario_path: str) -> dict[str, Any]:
    container_script = '''
import hashlib
import json
import subprocess
import time

iterations = __ITERATIONS__
scenario = "__SCENARIO__"
latencies = []
hashes = []

for _ in range(iterations):
    started = time.perf_counter()
    completed = subprocess.run(
        [
            "/usr/local/bin/queueforge-sim",
            "--input",
            scenario,
            "--output",
            "-",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    latencies.append((time.perf_counter() - started) * 1000)
    parsed = json.loads(completed.stdout)
    canonical = json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    hashes.append(hashlib.sha256(canonical).hexdigest())

print(json.dumps({
    "iterations": iterations,
    "latenciesMilliseconds": latencies,
    "uniqueResultHashes": sorted(set(hashes)),
}))
'''
    container_script = container_script.replace(
        "__ITERATIONS__",
        str(iterations),
    )
    container_script = container_script.replace(
        "__SCENARIO__",
        scenario_path,
    )

    completed = compose(
        "exec",
        "-T",
        "api",
        "python",
        "-c",
        container_script,
        capture=True,
    )
    result = json.loads(completed.stdout)
    latencies = [float(value) for value in result["latenciesMilliseconds"]]
    hashes = result["uniqueResultHashes"]
    return {
        "iterations": iterations,
        "minimumMilliseconds": min(latencies),
        "medianMilliseconds": percentile(latencies, 0.50),
        "p95Milliseconds": percentile(latencies, 0.95),
        "maximumMilliseconds": max(latencies),
        "deterministic": len(hashes) == 1,
        "resultHash": hashes[0] if len(hashes) == 1 else None,
    }


def benchmark_analytics(runs: int, scenario_path: str) -> dict[str, Any]:
    compose(
        "exec",
        "-T",
        "api",
        "rm",
        "-rf",
        "/tmp/queueforge-phase7-analytics",
    )
    started = time.perf_counter()
    compose(
        "exec",
        "-T",
        "api",
        "python",
        "-m",
        "queueforge_analytics",
        "experiment",
        "--scenario",
        scenario_path,
        "--output-dir",
        "/tmp/queueforge-phase7-analytics",
        "--server-counts",
        "3,4,5",
        "--runs",
        str(runs),
        "--seed-start",
        "20260801",
        "--engine",
        "/usr/local/bin/queueforge-sim",
    )
    elapsed = time.perf_counter() - started

    container_id = compose("ps", "-q", "api", capture=True).stdout.strip()
    report_path = RUNTIME / "staffing-comparison.json"
    run(
        [
            "docker",
            "cp",
            (
                f"{container_id}:"
                "/tmp/queueforge-phase7-analytics/staffing-comparison.json"
            ),
            str(report_path),
        ]
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = report.get("rows", report.get("results", []))
    return {
        "runsPerServerCount": runs,
        "serverCounts": [3, 4, 5],
        "elapsedSeconds": elapsed,
        "reportRows": len(rows) if isinstance(rows, list) else 0,
        "reportPath": str(report_path.relative_to(ROOT)),
    }


def execute_api_run(scenario: dict[str, Any]) -> dict[str, Any]:
    overall_started = time.perf_counter()
    submit_started = time.perf_counter()
    attempts = 0

    while True:
        attempts += 1
        status, headers, body = request(
            API + "/api/runs",
            method="POST",
            payload={"type": "SIMULATION", "scenario": scenario},
        )
        if status == 202:
            run_record = json.loads(body)
            break
        if status == 429 and attempts < 20:
            delay = float(headers.get("Retry-After", "1"))
            time.sleep(min(delay, 2))
            continue
        raise RuntimeError(
            f"Simulation submission returned {status}: "
            f"{body.decode(errors='replace')}"
        )

    submit_ms = (time.perf_counter() - submit_started) * 1000
    run_id = run_record["id"]
    deadline = time.monotonic() + 45

    while time.monotonic() < deadline:
        _, _, current = json_request(f"/api/runs/{run_id}")
        status_name = current.get("status")
        if status_name == "SUCCEEDED":
            return {
                "id": run_id,
                "submitMilliseconds": submit_ms,
                "endToEndMilliseconds": (
                    time.perf_counter() - overall_started
                )
                * 1000,
                "attempts": attempts,
                "status": status_name,
            }
        if status_name in {"FAILED", "CANCELLED"}:
            raise RuntimeError(f"Benchmark run became {status_name}: {current}")
        time.sleep(0.1)

    raise RuntimeError(f"Benchmark run did not complete: {run_id}")


def benchmark_api(
    scenario: dict[str, Any],
    runs: int,
    concurrency: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    results: list[dict[str, Any]] = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrency,
    ) as executor:
        futures = [
            executor.submit(execute_api_run, scenario)
            for _ in range(runs)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    submit = [float(result["submitMilliseconds"]) for result in results]
    end_to_end = [
        float(result["endToEndMilliseconds"])
        for result in results
    ]
    succeeded = sum(result["status"] == "SUCCEEDED" for result in results)
    return {
        "runs": runs,
        "concurrency": concurrency,
        "successRate": succeeded / runs,
        "submitMedianMilliseconds": percentile(submit, 0.50),
        "submitP95Milliseconds": percentile(submit, 0.95),
        "endToEndMedianMilliseconds": percentile(end_to_end, 0.50),
        "endToEndP95Milliseconds": percentile(end_to_end, 0.95),
        "wallSeconds": time.perf_counter() - started,
        "totalSubmissionAttempts": sum(
            int(result["attempts"])
            for result in results
        ),
    }


def benchmark_web() -> dict[str, Any]:
    status, _, html_body = request(WEB)
    if status != 200:
        raise RuntimeError(f"Web root returned {status}")
    html = html_body.decode()

    scripts = re.findall(r'<script[^>]+src="([^"]+\.js)"', html)
    styles = re.findall(r'href="([^"]+\.css)"', html)
    if not scripts:
        raise RuntimeError("No production JavaScript asset was found")

    def total_bytes(paths: list[str]) -> int:
        total = 0
        for path in paths:
            url = urllib.parse.urljoin(WEB + "/", path)
            asset_status, _, body = request(url)
            if asset_status != 200:
                raise RuntimeError(f"Asset returned {asset_status}: {url}")
            total += len(body)
        return total

    return {
        "javascriptAssets": len(scripts),
        "javascriptBytes": total_bytes(scripts),
        "cssAssets": len(styles),
        "cssBytes": total_bytes(styles),
    }


def image_size(name: str) -> int:
    output = docker_output(
        "image",
        "inspect",
        name,
        "--format",
        "{{.Size}}",
    )
    return int(output)


def gate(
    name: str,
    actual: Any,
    budget: Any,
    passed: bool,
    unit: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "actual": actual,
        "budget": budget,
        "unit": unit,
        "passed": passed,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 7 Performance Report",
        "",
        f"- Generated: {report['generatedAt']}",
        f"- Commit: `{report['environment']['gitCommit']}`",
        f"- Platform: {report['environment']['platform']}",
        f"- Architecture: {report['environment']['architecture']}",
        f"- Overall: {'PASS' if report['passed'] else 'FAIL'}",
        "",
        "| Gate | Actual | Budget | Result |",
        "|---|---:|---:|---|",
    ]
    for item in report["gates"]:
        lines.append(
            f"| `{item['name']}` | {item['actual']} {item['unit']} | "
            f"{item['budget']} {item['unit']} | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "These are portable regression budgets measured through Docker on "
            "the current host. They are not production SLOs or capacity claims.",
            "",
        ]
    )
    return "\n".join(lines)


budgets = json.loads(BUDGETS_PATH.read_text(encoding="utf-8"))
scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))

compose(
    "up",
    "-d",
    "--build",
    "--force-recreate",
    "postgres",
    "api",
    "web",
)
readiness = wait_ready()
scenario_in_container = copy_scenario_to_api()

cpp = benchmark_cpp(
    int(budgets["cpp"]["iterations"]),
    scenario_in_container,
)
analytics = benchmark_analytics(
    int(budgets["analytics"]["runs"]),
    scenario_in_container,
)
api = benchmark_api(
    scenario,
    int(budgets["api"]["runs"]),
    int(budgets["api"]["concurrency"]),
)
web = benchmark_web()
images = {
    "apiBytes": image_size("queueforge-api:latest"),
    "webBytes": image_size("queueforge-web:latest"),
}

gates = [
    gate(
        "cpp_determinism",
        cpp["deterministic"],
        True,
        cpp["deterministic"] is True,
        "boolean",
    ),
    gate(
        "cpp_p95",
        round(cpp["p95Milliseconds"], 3),
        budgets["cpp"]["p95MillisecondsMax"],
        cpp["p95Milliseconds"]
        <= float(budgets["cpp"]["p95MillisecondsMax"]),
        "ms",
    ),
    gate(
        "analytics_elapsed",
        round(analytics["elapsedSeconds"], 3),
        budgets["analytics"]["elapsedSecondsMax"],
        analytics["elapsedSeconds"]
        <= float(budgets["analytics"]["elapsedSecondsMax"]),
        "s",
    ),
    gate(
        "api_success_rate",
        round(api["successRate"], 4),
        budgets["api"]["successRateMin"],
        api["successRate"]
        >= float(budgets["api"]["successRateMin"]),
        "ratio",
    ),
    gate(
        "api_submit_p95",
        round(api["submitP95Milliseconds"], 3),
        budgets["api"]["submitP95MillisecondsMax"],
        api["submitP95Milliseconds"]
        <= float(budgets["api"]["submitP95MillisecondsMax"]),
        "ms",
    ),
    gate(
        "api_end_to_end_p95",
        round(api["endToEndP95Milliseconds"], 3),
        budgets["api"]["endToEndP95MillisecondsMax"],
        api["endToEndP95Milliseconds"]
        <= float(budgets["api"]["endToEndP95MillisecondsMax"]),
        "ms",
    ),
    gate(
        "web_javascript_size",
        web["javascriptBytes"],
        budgets["web"]["javascriptBytesMax"],
        web["javascriptBytes"]
        <= int(budgets["web"]["javascriptBytesMax"]),
        "bytes",
    ),
    gate(
        "web_css_size",
        web["cssBytes"],
        budgets["web"]["cssBytesMax"],
        web["cssBytes"]
        <= int(budgets["web"]["cssBytesMax"]),
        "bytes",
    ),
    gate(
        "api_image_size",
        images["apiBytes"],
        budgets["images"]["apiBytesMax"],
        images["apiBytes"]
        <= int(budgets["images"]["apiBytesMax"]),
        "bytes",
    ),
    gate(
        "web_image_size",
        images["webBytes"],
        budgets["images"]["webBytesMax"],
        images["webBytes"]
        <= int(budgets["images"]["webBytesMax"]),
        "bytes",
    ),
]

report = {
    "schemaVersion": "1.0",
    "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
    "environment": {
        "gitCommit": git_output("rev-parse", "HEAD"),
        "gitBranch": git_output("branch", "--show-current"),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "dockerServer": docker_output(
            "version",
            "--format",
            "{{.Server.Version}}",
        ),
    },
    "scenario": str(SCENARIO.relative_to(ROOT)),
    "budgets": budgets,
    "readiness": readiness,
    "measurements": {
        "cpp": cpp,
        "analytics": analytics,
        "api": api,
        "web": web,
        "images": images,
    },
    "gates": gates,
    "passed": all(item["passed"] for item in gates),
}

json_path = RUNTIME / "performance-report.json"
markdown_path = RUNTIME / "performance-report.md"
json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
markdown_path.write_text(markdown(report), encoding="utf-8")

print(f"Performance JSON: {json_path}")
print(f"Performance Markdown: {markdown_path}")
for item in gates:
    print(
        f"{'PASS' if item['passed'] else 'FAIL'} "
        f"{item['name']}: {item['actual']} / {item['budget']} {item['unit']}"
    )
