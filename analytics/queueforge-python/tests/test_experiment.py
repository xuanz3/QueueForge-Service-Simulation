from __future__ import annotations

from pathlib import Path
import unittest

from queueforge_analytics.experiment import TargetPolicy, run_experiment


def fake_runner(*, engine_path, scenario, seed, server_count):
    del engine_path, scenario
    overloaded = server_count == 3
    return {
        "schemaVersion": "1.0",
        "seed": seed,
        "invariants": {
            "accountingBalanced": True,
            "chronologyValid": True,
            "utilisationWithinRange": True,
        },
        "metrics": {
            "arrived": 192,
            "completed": 180 if overloaded else 191,
            "waitingAtEnd": 10 if overloaded else 0,
            "inServiceAtEnd": 2 if overloaded else 1,
            "averageWaitMinutes": 18.0 if overloaded else 2.0,
            "p95WaitMinutes": 30.0 if overloaded else 5.0,
            "maximumWaitMinutes": 40.0 if overloaded else 7.0,
            "averageQueueLength": 15.0 if overloaded else 1.0,
            "maximumQueueLength": 40 if overloaded else 4,
            "throughputPerHour": 22.5 if overloaded else 23.875,
            "overallUtilisation": 0.95 if overloaded else 0.72,
        },
    }


class ExperimentTest(unittest.TestCase):
    def test_selects_lowest_eligible_variant(self) -> None:
        scenario = {
            "simulation": {"durationMinutes": 480, "seed": 1},
            "arrivals": {"ratePerHour": 24},
            "service": {
                "minimumMinutes": 3,
                "modeMinutes": 6,
                "maximumMinutes": 12,
            },
            "queue": {"serverCount": 4},
        }
        report = run_experiment(
            scenario=scenario,
            engine_path=Path("unused"),
            server_counts=[3, 4, 5],
            run_count=4,
            seed_start=100,
            target=TargetPolicy(),
            runner=fake_runner,
        )
        self.assertEqual("meets_demo_target", report["recommendation"]["status"])
        self.assertEqual(4, report["recommendation"]["serverCount"])
        self.assertEqual(12, len(report["runs"]))


if __name__ == "__main__":
    unittest.main()
