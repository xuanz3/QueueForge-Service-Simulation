from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "phase6"
RUNTIME.mkdir(parents=True, exist_ok=True)

API = "http://localhost:18086"
WEB = "http://localhost:15176"
FAULT_KEYS = {
    "QUEUEFORGE_SIMULATION_COMMAND",
    "QUEUEFORGE_WORKER_TIMEOUT",
    "QUEUEFORGE_WORKER_CONCURRENCY",
    "QUEUEFORGE_WORKER_QUEUE_CAPACITY",
    "QUEUEFORGE_FAULT_DELAY_SECONDS",
}


def environment(**values: str) -> dict[str, str]:
    result = os.environ.copy()
    for key in FAULT_KEYS:
        result.pop(key, None)
    result.update(values)
    return result


def compose(args: list[str], env: dict[str, str]) -> None:
    subprocess.run(
        ["docker", "compose", *args],
        cwd=ROOT,
        env=env,
        check=True,
    )


def request(
    url: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    data = None if payload is None else json.dumps(payload).encode()
    request_headers = {"Accept": "application/json"}
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=request_headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
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
        raise AssertionError(
            f"{method} {path} returned {status}: {body.decode(errors='replace')}"
        )
    parsed = json.loads(body) if body else {}
    if not isinstance(parsed, dict):
        raise AssertionError(f"{path} did not return a JSON object")
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
    raise RuntimeError("API readiness did not become UP") from last


def recreate_api(env: dict[str, str]) -> dict[str, Any]:
    compose(["up", "-d", "--force-recreate", "api"], env)
    return wait_ready()


def load_scenario() -> dict[str, Any]:
    return json.loads(
        (ROOT / "contracts/examples/basic-scenario.json").read_text(
            encoding="utf-8"
        )
    )


def create_run() -> dict[str, Any]:
    _, _, body = json_request(
        "/api/runs",
        method="POST",
        payload={"type": "SIMULATION", "scenario": load_scenario()},
        expected={202},
    )
    return body


def wait_status(
    run_id: str,
    statuses: set[str],
    attempts: int = 120,
) -> dict[str, Any]:
    last: dict[str, Any] | None = None
    for _ in range(attempts):
        _, _, last = json_request(f"/api/runs/{run_id}")
        if last.get("status") in statuses:
            return last
        time.sleep(1)
    raise AssertionError(
        f"Run {run_id} did not reach {sorted(statuses)}; last={last}"
    )


def cancel(run_id: str) -> dict[str, Any]:
    _, _, body = json_request(
        f"/api/runs/{run_id}/cancel",
        method="POST",
        expected={202},
    )
    return body


def web_bundle() -> dict[str, Any]:
    status, _, html_body = request(WEB)
    assert status == 200, status
    html = html_body.decode()
    asset_match = re.search(r'<script[^>]+src="([^"]+\.js)"', html)
    assert asset_match, html[:500]
    asset_url = asset_match.group(1)
    if asset_url.startswith("/"):
        asset_url = WEB + asset_url
    asset_status, _, bundle_body = request(asset_url)
    assert asset_status == 200, asset_status
    bundle = bundle_body.decode()
    for marker in [
        "Operations studio",
        "Compare staffing options",
        "Test staffing decisions",
    ]:
        assert marker in bundle, marker
    return {"root": WEB, "asset": asset_url}


evidence: dict[str, Any] = {}

normal = environment()
compose(["up", "-d", "--build", "--force-recreate", "postgres", "api", "web"], normal)
evidence["initialReadiness"] = wait_ready()
evidence["web"] = web_bundle()

cors_status, cors_headers, _ = request(
    API + "/api/runs",
    method="OPTIONS",
    headers={
        "Origin": WEB,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    },
)
assert cors_status in {200, 204}, cors_status
assert cors_headers.get("Access-Control-Allow-Origin") == WEB, cors_headers
evidence["cors"] = {"status": cors_status, "origin": WEB}

normal_run = create_run()
normal_terminal = wait_status(normal_run["id"], {"SUCCEEDED", "FAILED", "CANCELLED"})
assert normal_terminal["status"] == "SUCCEEDED", normal_terminal
evidence["normalRun"] = normal_terminal

prometheus_status, _, prometheus_body = request(API + "/actuator/prometheus")
assert prometheus_status == 200, prometheus_status
prometheus = prometheus_body.decode()
for metric in [
    "queueforge_runs_submitted_total",
    "queueforge_runs_succeeded_total",
    "queueforge_runs_active",
]:
    assert metric in prometheus, metric
evidence["metrics"] = {
    "submitted": "queueforge_runs_submitted_total" in prometheus,
    "succeeded": "queueforge_runs_succeeded_total" in prometheus,
    "active": "queueforge_runs_active" in prometheus,
}

capacity_env = environment(
    QUEUEFORGE_SIMULATION_COMMAND="/opt/queueforge-faults/slow-simulation.sh",
    QUEUEFORGE_WORKER_TIMEOUT="PT45S",
    QUEUEFORGE_WORKER_CONCURRENCY="1",
    QUEUEFORGE_WORKER_QUEUE_CAPACITY="1",
    QUEUEFORGE_FAULT_DELAY_SECONDS="20",
)
recreate_api(capacity_env)
first = create_run()
second = create_run()
status, headers, problem = json_request(
    "/api/runs",
    method="POST",
    payload={"type": "SIMULATION", "scenario": load_scenario()},
    expected={429},
)
assert problem.get("title") == "Run capacity exhausted", problem
assert headers.get("Retry-After") == "2", headers
_, _, saturated_status = json_request("/api/system/status")
capacity = saturated_status.get("capacity", {})
assert capacity.get("maximum") == 2, capacity
assert capacity.get("available") == 0, capacity
cancel(first["id"])
cancel(second["id"])
wait_status(first["id"], {"CANCELLED"})
wait_status(second["id"], {"CANCELLED"})
evidence["capacity"] = {
    "httpStatus": status,
    "problem": problem,
    "snapshot": capacity,
}

failure_env = environment(
    QUEUEFORGE_SIMULATION_COMMAND="/opt/queueforge-faults/failing-simulation.sh",
    QUEUEFORGE_WORKER_TIMEOUT="PT10S",
    QUEUEFORGE_WORKER_CONCURRENCY="1",
    QUEUEFORGE_WORKER_QUEUE_CAPACITY="1",
)
recreate_api(failure_env)
failed = create_run()
failed_terminal = wait_status(failed["id"], {"FAILED"})
assert failed_terminal.get("errorCode") == "WORKER_EXIT_23", failed_terminal
evidence["workerFailure"] = failed_terminal

timeout_env = environment(
    QUEUEFORGE_SIMULATION_COMMAND="/opt/queueforge-faults/hanging-simulation.sh",
    QUEUEFORGE_WORKER_TIMEOUT="PT2S",
    QUEUEFORGE_WORKER_CONCURRENCY="1",
    QUEUEFORGE_WORKER_QUEUE_CAPACITY="1",
    QUEUEFORGE_FAULT_DELAY_SECONDS="60",
)
recreate_api(timeout_env)
timed_out = create_run()
timeout_terminal = wait_status(timed_out["id"], {"FAILED"}, attempts=60)
assert timeout_terminal.get("errorCode") == "WORKER_TIMEOUT", timeout_terminal
evidence["timeout"] = timeout_terminal

recovery_env = environment(
    QUEUEFORGE_SIMULATION_COMMAND="/opt/queueforge-faults/slow-simulation.sh",
    QUEUEFORGE_WORKER_TIMEOUT="PT45S",
    QUEUEFORGE_WORKER_CONCURRENCY="1",
    QUEUEFORGE_WORKER_QUEUE_CAPACITY="1",
    QUEUEFORGE_FAULT_DELAY_SECONDS="30",
)
recreate_api(recovery_env)
interrupted = create_run()
wait_status(interrupted["id"], {"RUNNING"}, attempts=30)
compose(["restart", "api"], recovery_env)
wait_ready()
recovered_terminal = wait_status(interrupted["id"], {"FAILED"}, attempts=60)
assert recovered_terminal.get("errorCode") == "CONTROL_PLANE_RESTARTED", recovered_terminal
_, _, recovery_status = json_request("/api/system/status")
recovered_count = recovery_status.get("telemetry", {}).get("recovered", 0)
assert recovered_count >= 1, recovery_status
evidence["restartRecovery"] = {
    "run": recovered_terminal,
    "telemetry": recovery_status.get("telemetry"),
}

compose(["up", "-d", "--build", "--force-recreate", "postgres", "api", "web"], normal)
wait_ready()
restored_run = create_run()
restored_terminal = wait_status(restored_run["id"], {"SUCCEEDED", "FAILED", "CANCELLED"})
assert restored_terminal["status"] == "SUCCEEDED", restored_terminal
evidence["restoredNormalRun"] = restored_terminal
evidence["restoredWeb"] = web_bundle()

(RUNTIME / "reliability-evidence.json").write_text(
    json.dumps(evidence, indent=2),
    encoding="utf-8",
)

print("Actuator readiness and Prometheus metrics: passed")
print("Browser-origin CORS: passed")
print("Capacity exhaustion and HTTP 429: passed")
print("Injected worker exit: passed")
print("Injected worker timeout: passed")
print("API restart reconciliation: passed")
print("Normal stack restoration: passed")
print("Phase 6 runtime verification passed.")
