from dataclasses import asdict, dataclass
import json, platform
@dataclass(frozen=True, slots=True)
class HealthStatus:
    service: str
    version: str
    status: str
    python_version: str
    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True)
def build_health_status() -> HealthStatus:
    return HealthStatus("queueforge-analytics", "0.1.0", "ready", platform.python_version())
