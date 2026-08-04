from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "phase5"
RUNTIME.mkdir(parents=True, exist_ok=True)

WEB = "http://localhost:15176"
API = "http://localhost:18086"


def request(url: str, method: str = "GET", payload: object | None = None) -> object:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(body)
        return body.decode()


def wait(url: str, attempts: int = 90) -> object:
    last: Exception | None = None
    for _ in range(attempts):
        try:
            return request(url)
        except Exception as exc:
            last = exc
            time.sleep(2)
    raise RuntimeError(f"Endpoint did not become ready: {url}") from last


status = wait(f"{API}/api/system/status")
assert isinstance(status, dict)
assert status["status"] == "ready", status
assert status["database"] == "ready", status

html = wait(WEB)
assert isinstance(html, str)
asset_match = re.search(r'<script[^>]+src="([^"]+\.js)"', html)
assert asset_match, html[:500]
asset_url = asset_match.group(1)
if asset_url.startswith("/"):
    asset_url = WEB + asset_url
bundle = request(asset_url)
assert isinstance(bundle, str)
for marker in [
    "Operations studio",
    "Compare staffing options",
    "Test staffing decisions",
]:
    assert marker in bundle, f"Deployed bundle is missing marker: {marker}"

scenario = json.loads(
    (ROOT / "contracts/examples/basic-scenario.json").read_text(encoding="utf-8")
)
created = request(
    f"{API}/api/runs",
    method="POST",
    payload={"type": "SIMULATION", "scenario": scenario},
)
assert isinstance(created, dict)
run_id = created["id"]

terminal = None
for _ in range(120):
    terminal = request(f"{API}/api/runs/{run_id}")
    assert isinstance(terminal, dict)
    if terminal["status"] in {"SUCCEEDED", "FAILED", "CANCELLED"}:
        break
    time.sleep(1)

assert terminal and terminal["status"] == "SUCCEEDED", terminal
result = request(f"{API}/api/runs/{run_id}/result")
assert isinstance(result, dict)
assert result["invariants"]["accountingBalanced"] is True
assert result["invariants"]["chronologyValid"] is True
assert result["invariants"]["utilisationWithinRange"] is True

evidence = {
    "status": "passed",
    "web": {
        "url": WEB,
        "asset": asset_url,
        "markers": [
            "Operations studio",
            "Compare staffing options",
            "Test staffing decisions",
        ],
    },
    "api": status,
    "run": terminal,
    "resultInvariants": result["invariants"],
}
(RUNTIME / "ui-runtime-evidence.json").write_text(
    json.dumps(evidence, indent=2), encoding="utf-8"
)

print("Deployed React bundle: passed")
print("Control-plane readiness: passed")
print("UI-backed simulation contract: passed")
print("Phase 5 runtime verification passed.")
