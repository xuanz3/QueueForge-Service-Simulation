from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import platform


@dataclass(frozen=True, slots=True)
class HealthStatus:
    service: str
    version: str
    status: str
    python_version: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True)


def build_health_status() -> HealthStatus:
    return HealthStatus(
        service="queueforge-analytics",
        version="0.2.0",
        status="ready",
        python_version=platform.python_version(),
    )
