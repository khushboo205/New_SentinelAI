"""
Unit tests for SentinelAI Core Models and Packets.
"""

import unittest
from datetime import datetime

from core.models import Detection, Feature, ReIDResult, Track
from core.packet import (
    BasePacket,
    DetectionPacket,
    FeaturePacket,
    FramePacket,
    ReIDPacket,
    TrackingPacket,
)


class TestModels(unittest.TestCase):

    def test_detection_dataclass_and_slots(self):
        d = Detection(
            bbox=(10.0, 20.0, 100.0, 200.0),
            confidence=0.88,
            class_id=0,
            class_name="person",
        )
        self.assertEqual(d.class_name, "person")
        self.assertEqual(d.class_id, 0)
        self.assertEqual(d.confidence, 0.88)
        self.assertEqual(d.bbox, (10.0, 20.0, 100.0, 200.0))

        # Dynamic attributes assigned by downstream agents must not raise AttributeError
        d.risk_score = 75.0
        d.risk_level = "Critical"
        d.alert = True
        d.is_suspicious = True
        d.reasons = ["Restricted Zone Intrusion"]
        d.contributing_factors = [{"factor": "restricted_zone", "weight": 35}]
        d.ocr_text = ["ABC1234"]
        d.ocr_confidence = 0.95
        d.zone = "Restricted Outer Perimeter"
        d.is_loitering = True
        d.speed_kmh = 12.5

        self.assertEqual(d.risk_level, "Critical")
        self.assertTrue(d.alert)
        self.assertEqual(d.zone, "Restricted Outer Perimeter")
        self.assertEqual(d.ocr_confidence, 0.95)

    def test_detection_to_dict(self):
        d = Detection(
            bbox=(0.0, 0.0, 50.0, 50.0),
            confidence=0.92351,
            class_id=2,
            class_name="car",
            risk_score=45.678,
            risk_level="Medium",
        )
        data = d.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["class_name"], "car")
        self.assertEqual(data["confidence"], 0.9235)
        self.assertEqual(data["risk_level"], "Medium")
        self.assertEqual(data["bbox"], [0.0, 0.0, 50.0, 50.0])

    def test_track_dataclass(self):
        d = Detection(
            bbox=(5.0, 5.0, 60.0, 80.0),
            confidence=0.85,
            class_id=0,
            class_name="person",
        )
        t = Track(track_id=42, detection=d, first_seen=1, last_seen=5, active=True)
        self.assertEqual(t.track_id, 42)
        self.assertEqual(t.detection.class_name, "person")
        self.assertTrue(t.active)

    def test_reid_and_feature(self):
        reid = ReIDResult(track_id=1, identity="SUBJECT_01", similarity=0.92)
        self.assertEqual(reid.identity, "SUBJECT_01")
        self.assertEqual(reid.similarity, 0.92)

        feat = Feature(track_id=1, shirt_color="blue", bag=True)
        self.assertEqual(feat.shirt_color, "blue")
        self.assertTrue(feat.bag)


class TestPackets(unittest.TestCase):

    def test_frame_packet_and_compatibility_property(self):
        fp = FramePacket(frame_id=101, width=1920, height=1080, fps=25.0)
        self.assertEqual(fp.frame_id, 101)
        # Verify frame_number property getter
        self.assertEqual(fp.frame_number, 101)
        # Verify frame_number property setter
        fp.frame_number = 202
        self.assertEqual(fp.frame_id, 202)
        self.assertEqual(fp.frame_number, 202)

    def test_packet_hierarchy(self):
        fp = FramePacket(frame_id=1)
        d = Detection(bbox=(0, 0, 1, 1), confidence=0.9, class_id=0, class_name="person")
        dp = DetectionPacket(frame_packet=fp, detections=[d])
        self.assertEqual(len(dp.detections), 1)

        t = Track(track_id=1, detection=d)
        tp = TrackingPacket(frame_packet=fp, tracks=[t])
        self.assertEqual(len(tp.tracks), 1)
        self.assertEqual(tp.tracks[0].track_id, 1)

        rp = ReIDPacket(frame_packet=fp, reid_results=[ReIDResult(track_id=1)])
        self.assertEqual(len(rp.reid_results), 1)

        feat_p = FeaturePacket(frame_packet=fp, features=[Feature(track_id=1)])
        self.assertEqual(len(feat_p.features), 1)


if __name__ == "__main__":
    unittest.main()
