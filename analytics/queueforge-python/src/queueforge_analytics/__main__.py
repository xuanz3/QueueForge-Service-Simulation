from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from queueforge_analytics.experiment import TargetPolicy, run_experiment
from queueforge_analytics.health import build_health_status
from queueforge_analytics.reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="queueforge-analytics")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="Print component health as JSON")

    experiment = subparsers.add_parser(
        "experiment",
        help="Run a common-seed staffing comparison",
    )
    experiment.add_argument("--scenario", type=Path, required=True)
    experiment.add_argument("--output-dir", type=Path, required=True)
    experiment.add_argument("--server-counts", default="3,4,5")
    experiment.add_argument("--runs", type=int, default=40)
    experiment.add_argument("--seed-start", type=int, default=20260801)
    experiment.add_argument("--target-p95-wait", type=float, default=10.0)
    experiment.add_argument("--target-max-queue", type=int, default=20)
    experiment.add_argument("--target-max-utilisation", type=float, default=0.85)
    experiment.add_argument("--required-success-rate", type=float, default=0.90)
    experiment.add_argument(
        "--engine",
        type=Path,
        default=Path(os.environ.get("QUEUEFORGE_ENGINE_PATH", "/usr/local/bin/queueforge-sim")),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "health":
        print(build_health_status().to_json())
        return 0

    if args.command == "experiment":
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        server_counts = [
            int(value.strip())
            for value in args.server_counts.split(",")
            if value.strip()
        ]
        target = TargetPolicy(
            p95_wait_minutes=args.target_p95_wait,
            maximum_queue_length=args.target_max_queue,
            maximum_utilisation=args.target_max_utilisation,
            required_success_rate=args.required_success_rate,
        )
        report = run_experiment(
            scenario=scenario,
            engine_path=args.engine,
            server_counts=server_counts,
            run_count=args.runs,
            seed_start=args.seed_start,
            target=target,
        )
        paths = write_reports(report, args.output_dir)
        print(
            json.dumps(
                {
                    "status": "complete",
                    "recommendation": report["recommendation"],
                    "outputs": {name: str(path) for name, path in paths.items()},
                },
                sort_keys=True,
            )
        )
        return 0

    return 64


if __name__ == "__main__":
    raise SystemExit(main())
