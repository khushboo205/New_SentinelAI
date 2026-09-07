"""
Unit tests for Forensic Enhancement, Quality Assessment, and Provenance Hashing.
"""

import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from agents.enhancement import (
    EnhancementAgent,
    EnhancementDecisionEngine,
    ForensicProcessor,
    FrameAnalyzer,
)
from core.packet import FramePacket
from services.pipeline_service import PipelineService


class TestEnhancementAndForensics(unittest.TestCase):

    def setUp(self):
        # Create standard synthetic test frames (100x100 BGR)
        # Sharp high-contrast pattern
        self.sharp_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        self.sharp_frame[25:75, 25:75] = 255

        # Blurry frame
        self.blurry_frame = cv2.GaussianBlur(self.sharp_frame, (15, 15), 0)

        # Low light frame
        self.dark_frame = (self.sharp_frame * 0.1).astype(np.uint8)

        self.analyzer = FrameAnalyzer()
        self.decision_engine = EnhancementDecisionEngine(blur_threshold=100.0, quality_threshold=82.0)
        self.processor = ForensicProcessor(use_gpu=False)

    def test_frame_analyzer_metrics(self):
        sharp_metrics = self.analyzer.analyze(self.sharp_frame)
        blurry_metrics = self.analyzer.analyze(self.blurry_frame)

        # Sharp frame must have higher blur_score (Laplacian variance) than blurred
        self.assertGreater(sharp_metrics.blur_score, blurry_metrics.blur_score)
        self.assertGreater(sharp_metrics.brightness, 0.0)

        # Check serialization
        d = sharp_metrics.to_dict()
        self.assertIn("blur_score", d)
        self.assertIn("overall_quality", d)

    def test_enhancement_decision_engine(self):
        # Blurry frame should trigger deblurring
        blurry_metrics = self.analyzer.analyze(self.blurry_frame)
        plan = self.decision_engine.create_plan_from_quality(
            metrics=blurry_metrics,
            is_blurry_from_assessor=True,
            blur_score_from_assessor=blurry_metrics.blur_score,
        )
        self.assertTrue(plan.should_enhance)
        self.assertIn("deblurring", plan.operations)

        # Dark frame should trigger adaptive gamma or illumination
        dark_metrics = self.analyzer.analyze(self.dark_frame)
        plan_dark = self.decision_engine.create_plan_from_quality(metrics=dark_metrics)
        self.assertTrue(plan_dark.should_enhance)
        self.assertIn("adaptive_gamma", plan_dark.operations)

    def test_forensic_processor_operations(self):
        plan = self.decision_engine.create_plan_from_quality(
            metrics=self.analyzer.analyze(self.blurry_frame),
            is_blurry_from_assessor=True,
        )
        enhanced = self.processor.execute_plan(self.blurry_frame, plan)
        self.assertEqual(enhanced.shape, self.blurry_frame.shape)
        self.assertEqual(enhanced.dtype, np.uint8)

    def test_enhancement_agent_process(self):
        agent = EnhancementAgent(use_gpu=False)
        agent.initialize()

        fp = FramePacket(frame_id=1, frame=self.dark_frame.copy())
        processed_fp = agent.process(fp)

        self.assertIsNotNone(processed_fp)
        self.assertIn("enhancement", processed_fp.metadata)
        meta = processed_fp.metadata["enhancement"]
        self.assertIn("operations_applied", meta)
        self.assertIn("quality_after", meta)
        self.assertIsNotNone(processed_fp.frame)
        agent.shutdown()

    def test_forensic_sha256_provenance(self):
        # Write temporary binary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"SENTINELAI_EVIDENCE_STREAM_TEST")
            f_path = f.name

        try:
            h1 = PipelineService.compute_file_sha256(f_path)
            self.assertEqual(len(h1), 64)  # 256 bits = 64 hex characters
            # Idempotency
            h2 = PipelineService.compute_file_sha256(f_path)
            self.assertEqual(h1, h2)
        finally:
            Path(f_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
