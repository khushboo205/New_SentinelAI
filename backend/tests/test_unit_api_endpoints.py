"""
Unit tests for FastAPI REST Endpoints (direct handler execution).
"""

import asyncio
import unittest
from fastapi import HTTPException

from api.app import root
from api.routes.health import health
from api.routes.cameras import get_cameras, get_camera
from api.routes.risk import evaluate_risk, RiskEvaluationRequest
from api.routes.events import list_events, events_summary
from api.routes.analytics import summary as analytics_summary, hourly_activity


class TestAPIEndpoints(unittest.TestCase):

    def test_root_endpoint(self):
        data = asyncio.run(root())
        self.assertEqual(data["status"], "online")
        self.assertIn("SentinelAI", data["engine"])

    def test_health_endpoint(self):
        data = asyncio.run(health())
        self.assertEqual(data["status"], "healthy")

    def test_cameras_endpoints(self):
        # List cameras
        data = asyncio.run(get_cameras())
        self.assertIn("cameras", data)
        self.assertGreater(len(data["cameras"]), 0)

        # Single camera valid
        cam = asyncio.run(get_camera("CAM_01"))
        self.assertEqual(cam["id"], "CAM_01")

        # Single camera invalid
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(get_camera("INVALID_CAM_XYZ"))
        self.assertEqual(ctx.exception.status_code, 404)

    def test_risk_evaluate_endpoint(self):
        payload = RiskEvaluationRequest(
            night_period=True,
            restricted_zone=True,
            loitering=False,
        )
        data = asyncio.run(evaluate_risk(payload))
        self.assertEqual(data["composite_score"], 55)
        self.assertEqual(data["risk_level"], "High")
        self.assertTrue(data["is_suspicious"])
        self.assertEqual(len(data["contributing_factors"]), 2)

    def test_events_endpoints(self):
        # Summary
        data_sum = asyncio.run(events_summary())
        self.assertIn("total_events", data_sum)
        self.assertIn("total_tracks", data_sum)

        # List
        data_list = asyncio.run(list_events(limit=10, offset=0))
        self.assertIn("events", data_list)
        self.assertIn("count", data_list)

    def test_analytics_endpoints(self):
        data = asyncio.run(analytics_summary())
        self.assertIn("total_tracks", data)

        hourly_data = asyncio.run(hourly_activity())
        self.assertEqual(len(hourly_data), 24)


if __name__ == "__main__":
    unittest.main()

