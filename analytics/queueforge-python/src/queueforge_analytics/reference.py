from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class AnalyticalReference:
    expected_arrivals: float
    mean_service_minutes: float
    offered_load_erlangs: float
    nominal_utilisation: float
    stable_under_mean_load: bool

    def as_dict(self) -> dict[str, float | bool]:
        return asdict(self)


def build_reference(
    scenario: dict[str, Any],
    *,
    server_count: int,
) -> AnalyticalReference:
    duration = float(scenario["simulation"]["durationMinutes"])
    rate_per_hour = float(scenario["arrivals"]["ratePerHour"])
    service = scenario["service"]
    mean_service = (
        float(service["minimumMinutes"])
        + float(service["modeMinutes"])
        + float(service["maximumMinutes"])
    ) / 3.0

    expected_arrivals = rate_per_hour * duration / 60.0
    offered_load = rate_per_hour * mean_service / 60.0
    nominal_utilisation = offered_load / server_count

    return AnalyticalReference(
        expected_arrivals=expected_arrivals,
        mean_service_minutes=mean_service,
        offered_load_erlangs=offered_load,
        nominal_utilisation=nominal_utilisation,
        stable_under_mean_load=offered_load < server_count,
    )


def arrival_mean_tolerance(reference: AnalyticalReference, run_count: int) -> float:
    if run_count <= 0:
        raise ValueError("run_count must be positive")
    # Five standard errors of the Poisson run mean. This is deliberately
    # conservative and only checks gross engine/analytics disagreement.
    return 5.0 * math.sqrt(reference.expected_arrivals / run_count)
