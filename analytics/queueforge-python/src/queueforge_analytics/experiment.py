from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from queueforge_analytics.engine import run_engine
from queueforge_analytics.reference import arrival_mean_tolerance, build_reference
from queueforge_analytics.statistics import summarize


@dataclass(frozen=True, slots=True)
class TargetPolicy:
    p95_wait_minutes: float = 10.0
    maximum_queue_length: int = 20
    maximum_utilisation: float = 0.85
    required_success_rate: float = 0.90

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


Runner = Callable[..., dict[str, Any]]


def run_experiment(
    *,
    scenario: dict[str, Any],
    engine_path: Path,
    server_counts: list[int],
    run_count: int,
    seed_start: int,
    target: TargetPolicy,
    runner: Runner = run_engine,
) -> dict[str, Any]:
    if run_count < 2:
        raise ValueError("run_count must be at least 2")
    if not server_counts or any(count <= 0 for count in server_counts):
        raise ValueError("server_counts must contain positive integers")
    if len(set(server_counts)) != len(server_counts):
        raise ValueError("server_counts must not contain duplicates")

    seed_schedule = [seed_start + offset for offset in range(run_count)]
    run_records: list[dict[str, Any]] = []
    variant_summaries: list[dict[str, Any]] = []

    for server_count in sorted(server_counts):
        variant_runs: list[dict[str, Any]] = []

        for seed in seed_schedule:
            result = runner(
                engine_path=engine_path,
                scenario=scenario,
                seed=seed,
                server_count=server_count,
            )
            metrics = result["metrics"]
            record = {
                "serverCount": server_count,
                "seed": seed,
                "arrived": int(metrics["arrived"]),
                "completed": int(metrics["completed"]),
                "waitingAtEnd": int(metrics["waitingAtEnd"]),
                "inServiceAtEnd": int(metrics["inServiceAtEnd"]),
                "averageWaitMinutes": float(metrics["averageWaitMinutes"]),
                "p95WaitMinutes": float(metrics["p95WaitMinutes"]),
                "maximumWaitMinutes": float(metrics["maximumWaitMinutes"]),
                "averageQueueLength": float(metrics["averageQueueLength"]),
                "maximumQueueLength": int(metrics["maximumQueueLength"]),
                "throughputPerHour": float(metrics["throughputPerHour"]),
                "overallUtilisation": float(metrics["overallUtilisation"]),
            }
            record["meetsTarget"] = (
                record["p95WaitMinutes"] <= target.p95_wait_minutes
                and record["maximumQueueLength"] <= target.maximum_queue_length
                and record["overallUtilisation"] <= target.maximum_utilisation
            )
            variant_runs.append(record)
            run_records.append(record)

        reference = build_reference(scenario, server_count=server_count)
        arrivals = summarize(run["arrived"] for run in variant_runs)
        success_rate = sum(bool(run["meetsTarget"]) for run in variant_runs) / run_count

        variant_summaries.append(
            {
                "serverCount": server_count,
                "runCount": run_count,
                "successRate": success_rate,
                "meetsRequiredSuccessRate": success_rate >= target.required_success_rate,
                "metrics": {
                    "arrived": arrivals.as_dict(),
                    "completed": summarize(run["completed"] for run in variant_runs).as_dict(),
                    "averageWaitMinutes": summarize(
                        run["averageWaitMinutes"] for run in variant_runs
                    ).as_dict(),
                    "p95WaitMinutes": summarize(
                        run["p95WaitMinutes"] for run in variant_runs
                    ).as_dict(),
                    "maximumQueueLength": summarize(
                        run["maximumQueueLength"] for run in variant_runs
                    ).as_dict(),
                    "overallUtilisation": summarize(
                        run["overallUtilisation"] for run in variant_runs
                    ).as_dict(),
                    "throughputPerHour": summarize(
                        run["throughputPerHour"] for run in variant_runs
                    ).as_dict(),
                },
                "analyticalReference": reference.as_dict(),
                "arrivalMeanWithinReferenceTolerance": (
                    abs(arrivals.mean - reference.expected_arrivals)
                    <= arrival_mean_tolerance(reference, run_count)
                ),
            }
        )

    eligible = [
        item
        for item in variant_summaries
        if item["meetsRequiredSuccessRate"]
        and item["arrivalMeanWithinReferenceTolerance"]
    ]

    recommendation = (
        {
            "status": "meets_demo_target",
            "serverCount": min(item["serverCount"] for item in eligible),
            "statement": (
                "Lowest tested server count meeting the fictional target policy "
                "at the required observed success rate."
            ),
        }
        if eligible
        else {
            "status": "no_tested_variant_meets_demo_target",
            "serverCount": None,
            "statement": (
                "No tested server count met the fictional target policy at the "
                "required observed success rate."
            ),
        }
    )

    return {
        "schemaVersion": "1.0",
        "analyticsVersion": "0.2.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "experiment": {
            "runCountPerVariant": run_count,
            "seedStart": seed_start,
            "seedEnd": seed_schedule[-1],
            "commonRandomNumbers": True,
            "serverCounts": sorted(server_counts),
        },
        "targetPolicy": target.as_dict(),
        "decisionRule": (
            "Choose the lowest tested server count whose observed target success "
            "rate is at least the requiredSuccessRate. This is demonstration "
            "evidence for a fictional scenario, not operational advice."
        ),
        "recommendation": recommendation,
        "variants": variant_summaries,
        "runs": run_records,
        "limitations": [
            "The scenario and target policy are fictional.",
            "A 95% normal-approximation interval is used for run-level means.",
            "The analytical reference is a reasonableness check, not a queueing-theory oracle.",
            "Results apply only to the committed engine, inputs and seed schedule.",
        ],
    }
