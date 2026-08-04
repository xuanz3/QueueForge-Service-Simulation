from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from statistics import fmean, stdev
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Summary:
    count: int
    mean: float
    standard_deviation: float
    confidence_interval_95_low: float
    confidence_interval_95_high: float
    minimum: float
    median: float
    p95: float
    maximum: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


def nearest_rank(values: Iterable[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("at least one value is required")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0 and 1")

    if probability == 0:
        return ordered[0]
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[rank - 1]


def summarize(values: Iterable[float]) -> Summary:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("at least one value is required")

    count = len(ordered)
    mean = fmean(ordered)
    deviation = stdev(ordered) if count > 1 else 0.0
    margin = 1.96 * deviation / math.sqrt(count) if count > 1 else 0.0

    return Summary(
        count=count,
        mean=mean,
        standard_deviation=deviation,
        confidence_interval_95_low=mean - margin,
        confidence_interval_95_high=mean + margin,
        minimum=ordered[0],
        median=nearest_rank(ordered, 0.5),
        p95=nearest_rank(ordered, 0.95),
        maximum=ordered[-1],
    )
