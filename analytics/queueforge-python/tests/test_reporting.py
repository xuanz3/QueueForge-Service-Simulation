from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from queueforge_analytics.reporting import write_reports


class ReportingTest(unittest.TestCase):
    def test_writes_all_report_formats(self) -> None:
        report = {
            "recommendation": {
                "status": "meets_demo_target",
                "serverCount": 4,
                "statement": "Demonstration statement.",
            },
            "variants": [
                {
                    "serverCount": 4,
                    "runCount": 2,
                    "successRate": 1.0,
                    "meetsRequiredSuccessRate": True,
                    "arrivalMeanWithinReferenceTolerance": True,
                    "metrics": {
                        "p95WaitMinutes": {
                            "mean": 3.0,
                            "confidence_interval_95_low": 2.5,
                            "confidence_interval_95_high": 3.5,
                        },
                        "maximumQueueLength": {"mean": 4.0},
                        "overallUtilisation": {
                            "mean": 0.7,
                            "confidence_interval_95_low": 0.68,
                            "confidence_interval_95_high": 0.72,
                        },
                    },
                }
            ],
            "runs": [
                {
                    "serverCount": 4,
                    "seed": 1,
                    "meetsTarget": True,
                }
            ],
            "limitations": ["Synthetic scenario."],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            paths = write_reports(report, Path(temp_dir))
            self.assertEqual({"json", "variantCsv", "runCsv", "html"}, set(paths))
            for path in paths.values():
                self.assertTrue(path.is_file())
            loaded = json.loads(paths["json"].read_text())
            self.assertEqual(4, loaded["recommendation"]["serverCount"])


if __name__ == "__main__":
    unittest.main()
