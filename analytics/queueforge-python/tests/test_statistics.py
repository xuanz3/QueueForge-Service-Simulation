from __future__ import annotations

import unittest

from queueforge_analytics.statistics import nearest_rank, summarize


class StatisticsTest(unittest.TestCase):
    def test_nearest_rank(self) -> None:
        values = [1, 2, 3, 4, 5]
        self.assertEqual(3, nearest_rank(values, 0.5))
        self.assertEqual(5, nearest_rank(values, 0.95))

    def test_summary(self) -> None:
        result = summarize([1, 2, 3, 4])
        self.assertEqual(4, result.count)
        self.assertEqual(2.5, result.mean)
        self.assertLess(result.confidence_interval_95_low, result.mean)
        self.assertGreater(result.confidence_interval_95_high, result.mean)


if __name__ == "__main__":
    unittest.main()
