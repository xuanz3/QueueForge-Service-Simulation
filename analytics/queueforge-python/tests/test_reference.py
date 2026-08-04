from __future__ import annotations

import unittest

from queueforge_analytics.reference import build_reference


class ReferenceTest(unittest.TestCase):
    def test_basic_scenario_reference(self) -> None:
        scenario = {
            "simulation": {"durationMinutes": 480},
            "arrivals": {"ratePerHour": 24},
            "service": {
                "minimumMinutes": 3,
                "modeMinutes": 6,
                "maximumMinutes": 12,
            },
        }
        reference = build_reference(scenario, server_count=4)
        self.assertEqual(192, reference.expected_arrivals)
        self.assertEqual(7, reference.mean_service_minutes)
        self.assertAlmostEqual(2.8, reference.offered_load_erlangs)
        self.assertAlmostEqual(0.7, reference.nominal_utilisation)
        self.assertTrue(reference.stable_under_mean_load)


if __name__ == "__main__":
    unittest.main()
