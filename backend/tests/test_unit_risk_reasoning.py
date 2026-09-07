"""
Unit tests for Transparent Rule-Based Risk Engine, SuspicionAgent, and EventReasoningAgent.
"""

import unittest

from agents.event_reasoning_agent import EventReasoningAgent
from agents.suspicion_agent import RuleBasedRiskEngine, SuspicionAgent
from core.models import Detection, Track
from core.packet import FramePacket, TrackingPacket


class TestRiskAndReasoning(unittest.TestCase):

    def setUp(self):
        self.engine = RuleBasedRiskEngine()

    def test_baseline_risk_score(self):
        res = self.engine.evaluate()
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["risk_level"], "Low")
        self.assertFalse(res["is_suspicious"])
        self.assertEqual(len(res["contributing_factors"]), 0)

    def test_individual_factor_weights(self):
        # Restricted zone = 35 pts -> Medium
        r1 = self.engine.evaluate(restricted_zone=True)
        self.assertEqual(r1["score"], 35)
        self.assertEqual(r1["risk_level"], "Medium")

        # Night period = 20 pts -> Low
        r2 = self.engine.evaluate(night_period=True)
        self.assertEqual(r2["score"], 20)
        self.assertEqual(r2["risk_level"], "Low")

        # Loitering = 25 pts -> Medium
        r3 = self.engine.evaluate(loitering=True)
        self.assertEqual(r3["score"], 25)
        self.assertEqual(r3["risk_level"], "Medium")

        # High speed = 20 pts
        r4 = self.engine.evaluate(high_speed_movement=True)
        self.assertEqual(r4["score"], 20)

        # Unverified reid = 15 pts
        r5 = self.engine.evaluate(unverified_reid=True)
        self.assertEqual(r5["score"], 15)

        # Degraded footage = 15 pts
        r6 = self.engine.evaluate(degraded_footage=True)
        self.assertEqual(r6["score"], 15)

    def test_cumulative_score_and_clamping(self):
        # Restricted (35) + Loitering (25) = 60 -> High, suspicious
        r_high = self.engine.evaluate(restricted_zone=True, loitering=True)
        self.assertEqual(r_high["score"], 60)
        self.assertEqual(r_high["risk_level"], "High")
        self.assertTrue(r_high["is_suspicious"])

        # Restricted (35) + Loitering (25) + Night (20) = 80 -> Critical
        r_crit = self.engine.evaluate(restricted_zone=True, loitering=True, night_period=True)
        self.assertEqual(r_crit["score"], 80)
        self.assertEqual(r_crit["risk_level"], "Critical")

        # All factors combined -> Clamped to 100
        r_all = self.engine.evaluate(
            night_period=True,
            restricted_zone=True,
            loitering=True,
            degraded_footage=True,
            unverified_reid=True,
            high_speed_movement=True,
        )
        self.assertEqual(r_all["score"], 100)
        self.assertEqual(r_all["risk_level"], "Critical")
        self.assertGreater(r_all["raw_score"], 100)

    def test_suspicion_agent_packet_processing(self):
        agent = SuspicionAgent()
        agent.initialize()

        d = Detection(
            bbox=(0, 0, 10, 10),
            confidence=0.9,
            class_id=0,
            class_name="person",
            zone="Restricted Outer Perimeter Buffer",
            is_loitering=True,
        )
        t = Track(track_id=1, detection=d)
        tp = TrackingPacket(frame_packet=FramePacket(frame_id=1), tracks=[t])

        processed_tp = agent.process(tp)
        det = processed_tp.tracks[0].detection

        self.assertGreaterEqual(det.risk_score, 35)  # restricted zone triggered
        self.assertIn(det.risk_level, ["Medium", "High", "Critical"])
        self.assertIsInstance(det.reasons, list)
        self.assertGreater(len(det.contributing_factors), 0)
        agent.shutdown()

    def test_event_reasoning_truthfulness_no_fake_weapons(self):
        agent = EventReasoningAgent()
        agent.initialize()

        # Normal person walking
        d_person = Detection(
            bbox=(0, 0, 10, 10),
            confidence=0.9,
            class_id=0,
            class_name="person",
            behavior={"running": True, "restricted": True},
        )
        t_person = Track(track_id=1, detection=d_person)

        # Backpack unattended
        d_bag = Detection(
            bbox=(0, 0, 5, 5),
            confidence=0.85,
            class_id=24,
            class_name="backpack",
            behavior={"dwell_time": 75, "speed": 0.5},
        )
        t_bag = Track(track_id=2, detection=d_bag)

        tp = TrackingPacket(frame_packet=FramePacket(frame_id=1), tracks=[t_person, t_bag])
        result = agent.process(tp)

        p_events = [ev["event"] for ev in result.tracks[0].detection.events]
        self.assertIn("Rapid Movement / Running", p_events)
        self.assertIn("Restricted Zone Intrusion", p_events)

        bag_events = [ev["event"] for ev in result.tracks[1].detection.events]
        self.assertIn("Unattended Baggage Detected", bag_events)

        # Verify no weapon / fire hallucination exists in event outputs
        all_event_names = p_events + bag_events
        for name in all_event_names:
            self.assertNotIn("Weapon", name)
            self.assertNotIn("Fire", name)
            self.assertNotIn("Smoke", name)

        agent.shutdown()


if __name__ == "__main__":
    unittest.main()
