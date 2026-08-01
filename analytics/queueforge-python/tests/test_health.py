import json, unittest
from queueforge_analytics.health import build_health_status
class HealthStatusTest(unittest.TestCase):
    def test_payload(self):
        payload = json.loads(build_health_status().to_json())
        self.assertEqual("queueforge-analytics", payload["service"])
        self.assertEqual("ready", payload["status"])
if __name__ == "__main__": unittest.main()
