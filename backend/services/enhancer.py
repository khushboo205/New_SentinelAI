"""
SentinelAI Forensic Enhancer Service

Wraps ForensicProcessor, FrameAnalyzer, and EnhancementDecisionEngine
from agents/enhancement.py to provide robust, non-destructive forensic
enhancement for CCTV surveillance frames and ROIs.
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from agents.enhancement import (
    EnhancementDecisionEngine,
    EnhancementPlan,
    ForensicProcessor,
    FrameAnalyzer,
    FrameQualityMetrics,
)


class Enhancer:
    """
    Forensic Enhancer wrapping ForensicProcessor and FrameAnalyzer.
    Performs deterministic, non-destructive enhancement operations:
    CLAHE, unsharp masking, bilateral denoising, adaptive gamma, etc.
    """

    def __init__(
        self,
        blur_threshold: float = 100.0,
        quality_threshold: float = 82.0,
        use_gpu: bool = False,
    ) -> None:
        self.analyzer = FrameAnalyzer()
        self.decision_engine = EnhancementDecisionEngine(
            blur_threshold=blur_threshold,
            quality_threshold=quality_threshold,
        )
        self.processor = ForensicProcessor(use_gpu=use_gpu)

    def analyze(self, roi: np.ndarray) -> FrameQualityMetrics:
        """Analyze ROI quality and return quantitative metrics."""
        return self.analyzer.analyze(roi)

    def enhance(
        self,
        roi: np.ndarray,
        level: Optional[str] = None,
        operations: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Apply forensic enhancement to an image or ROI.

        Parameters:
            roi: BGR numpy array
            level: 'light', 'moderate', 'aggressive', or None (auto-detect)
            operations: specific list of operations to apply

        Returns:
            Enhanced BGR numpy array
        """
        if roi is None or roi.size == 0:
            return roi

        metrics = self.analyzer.analyze(roi)
        is_blurry = metrics.blur_score < 100.0

        if operations:
            plan = EnhancementPlan(
                should_enhance=True,
                enhancement_level="manual",
                operations=operations,
                assessor_diagnosis="Manual operator pipeline selection.",
            )
        elif level:
            lvl = level.lower().strip()
            if lvl == "light":
                plan = EnhancementPlan(
                    should_enhance=True,
                    enhancement_level="light",
                    operations=["adaptive_clahe", "adaptive_sharpening"],
                    assessor_diagnosis="Operator selected LIGHT enhancement profile.",
                )
            elif lvl == "aggressive":
                plan = EnhancementPlan(
                    should_enhance=True,
                    enhancement_level="aggressive",
                    operations=["adaptive_gamma", "shadow_recovery", "adaptive_clahe", "fast_denoising", "unsharp_masking"],
                    assessor_diagnosis="Operator selected AGGRESSIVE enhancement profile.",
                )
            else:  # moderate default
                plan = EnhancementPlan(
                    should_enhance=True,
                    enhancement_level="moderate",
                    operations=["adaptive_clahe", "fast_denoising", "adaptive_sharpening"],
                    assessor_diagnosis="Operator selected MODERATE enhancement profile.",
                )
        else:
            plan = self.decision_engine.create_plan_from_quality(
                metrics=metrics,
                is_blurry_from_assessor=is_blurry,
                blur_score_from_assessor=metrics.blur_score,
            )

        # Execute operations
        if plan.should_enhance:
            enhanced = self.processor.execute_plan(roi, plan)
            return enhanced
        else:
            # If auto plan suggested skip, return unmodified copy
            return roi.copy()

    def process_and_save(
        self,
        roi: np.ndarray,
        output_dir: str = "data/enhanced",
        level: str = "moderate",
    ) -> Dict[str, Any]:
        """
        Enhance ROI, compute SHA-256 hashes, verify difference, and save to disk.
        """
        os.makedirs(output_dir, exist_ok=True)
        t0 = time.perf_counter()

        success_orig, orig_buf = cv2.imencode(".jpg", roi, [cv2.IMWRITE_JPEG_QUALITY, 92])
        if not success_orig:
            raise ValueError("Failed to encode input frame")
        orig_bytes = orig_buf.tobytes()
        orig_hash = hashlib.sha256(orig_bytes).hexdigest()

        metrics_before = self.analyzer.analyze(roi)
        enhanced = self.enhance(roi, level=level)
        metrics_after = self.analyzer.analyze(enhanced)

        success_enh, enh_buf = cv2.imencode(".jpg", enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
        if not success_enh:
            raise ValueError("Failed to encode enhanced frame")
        enh_bytes = enh_buf.tobytes()
        enh_hash = hashlib.sha256(enh_bytes).hexdigest()

        # Save to disk
        filename = f"{enh_hash}.jpg"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(enh_bytes)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "before_hash": orig_hash,
            "after_hash": enh_hash,
            "hash_changed": (orig_hash != enh_hash),
            "file_path": filepath,
            "file_exists": os.path.exists(filepath),
            "file_size_bytes": len(enh_bytes),
            "processing_time_ms": round(elapsed_ms, 2),
            "quality_before": round(metrics_before.overall_quality, 1),
            "quality_after": round(metrics_after.overall_quality, 1),
            "metrics_before": metrics_before.to_dict(),
            "metrics_after": metrics_after.to_dict(),
        }