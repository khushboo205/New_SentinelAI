"""
SentinelAI Enhancement API Service

Exposes the FrameAnalyzer + EnhancementDecisionEngine + ForensicProcessor
as a single-image HTTP API service, independent of the full video pipeline.

This bridges the gap between the excellent existing enhancement code in
agents/enhancement.py and the HTTP API layer.
"""

from __future__ import annotations

import base64
import hashlib
import io
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from database.repository import Repository
except ImportError:
    from backend.database.repository import Repository

# Import the full implementation from agents/enhancement.py
try:
    from agents.enhancement import (
        FrameAnalyzer,
        EnhancementDecisionEngine,
        EnhancementPlan,
        FrameQualityMetrics,
        ForensicProcessor,
    )
except ImportError:
    from backend.agents.enhancement import (
        FrameAnalyzer,
        EnhancementDecisionEngine,
        EnhancementPlan,
        FrameQualityMetrics,
        ForensicProcessor,
    )


class EnhancementAPIService:
    """
    HTTP-facing service that wraps the ForensicProcessor pipeline
    for single-image enhancement requests.

    Design:
      analyze(image_bytes) -> QualityReport
      run(image_bytes, plan_override=None) -> EnhancementResult
    """

    def __init__(
        self,
        blur_threshold: float = 100.0,
        quality_threshold: float = 82.0,
    ) -> None:
        self.analyzer = FrameAnalyzer()
        self.decision_engine = EnhancementDecisionEngine(
            blur_threshold=blur_threshold,
            quality_threshold=quality_threshold,
        )
        self.processor = ForensicProcessor(use_gpu=False)
        self.repository = Repository()
        self._ready = True

    # ------------------------------------------------------------------
    # Decode helpers
    # ------------------------------------------------------------------

    def _decode_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Decode raw image bytes to a BGR numpy array."""
        try:
            arr = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return frame
        except Exception:
            return None

    def _encode_image(self, frame: np.ndarray, ext: str = ".jpg") -> bytes:
        """Encode a BGR numpy frame to JPEG/PNG bytes."""
        success, buf = cv2.imencode(ext, frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
        if not success:
            raise ValueError("Failed to encode enhanced frame")
        return buf.tobytes()

    def _sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    # ------------------------------------------------------------------
    # Diagnosis helpers
    # ------------------------------------------------------------------

    def _build_diagnosis(self, metrics: FrameQualityMetrics) -> List[Dict[str, str]]:
        """Build human-readable diagnosis chips from quality metrics."""
        diag: List[Dict[str, str]] = []

        if metrics.brightness < 60:
            diag.append({"label": "VERY LOW LIGHT", "severity": "critical"})
        elif metrics.brightness < 85:
            diag.append({"label": "LOW LIGHT", "severity": "high"})
        elif metrics.brightness > 210:
            diag.append({"label": "OVEREXPOSED", "severity": "high"})

        if metrics.blur_score < 50:
            diag.append({"label": "SEVERE MOTION BLUR", "severity": "critical"})
        elif metrics.blur_score < 100:
            diag.append({"label": "HIGH MOTION BLUR", "severity": "high"})

        if metrics.noise_score > 20:
            diag.append({"label": "HIGH NOISE", "severity": "high"})
        elif metrics.noise_score > 12:
            diag.append({"label": "MODERATE NOISE", "severity": "medium"})

        if metrics.compression_artifacts > 3.0:
            diag.append({"label": "COMPRESSION ARTIFACTS", "severity": "high"})
        elif metrics.compression_artifacts > 2.0:
            diag.append({"label": "MODERATE COMPRESSION", "severity": "medium"})

        if metrics.contrast < 30:
            diag.append({"label": "LOW CONTRAST", "severity": "high"})
        elif metrics.contrast < 38:
            diag.append({"label": "MODERATE CONTRAST", "severity": "medium"})

        if metrics.dynamic_range < 80:
            diag.append({"label": "NARROW DYNAMIC RANGE", "severity": "medium"})

        w, h = metrics.resolution
        if w < 480 or h < 360:
            diag.append({"label": "LOW RESOLUTION", "severity": "medium"})

        if not diag:
            diag.append({"label": "ACCEPTABLE QUALITY", "severity": "low"})

        return diag

    def _ops_to_display(self, ops: List[str]) -> List[Dict[str, str]]:
        """Convert internal operation names to user-readable pipeline steps."""
        labels = {
            "adaptive_gamma": "Low-light gamma correction",
            "shadow_recovery": "Shadow recovery",
            "exposure_correction": "Exposure correction",
            "highlight_recovery": "Highlight recovery",
            "adaptive_clahe": "Natural HDR tone mapping",
            "contrast_stretching": "Contrast stretching",
            "color_constancy": "White balance (gray-world)",
            "fast_denoising": "Bilateral denoising",
            "edge_preserving_filter": "Edge-preserving filter",
            "deblurring": "High-frequency kernel sharpening (3x3)",
            "unsharp_masking": "Unsharp masking",
            "adaptive_sharpening": "Adaptive sharpening",
            "laplacian_sharpening": "Laplacian detail boost",
            "flagship_isp": "Full ISP pipeline",
            "skip": "No enhancement required",
        }
        return [{"op": op, "label": labels.get(op, op)} for op in ops]

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def analyze(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze image quality and return metrics + diagnosis + recommended pipeline.
        Does NOT modify the image.
        """
        frame = self._decode_image(image_bytes)
        if frame is None:
            return {"error": "Could not decode image. Ensure it is a valid JPEG/PNG file."}

        h, w = frame.shape[:2]
        metrics = self.analyzer.analyze(frame)

        # Determine blur guidance for plan
        is_blurry = metrics.blur_score < 100.0

        plan = self.decision_engine.create_plan_from_quality(
            metrics=metrics,
            is_blurry_from_assessor=is_blurry,
            blur_score_from_assessor=metrics.blur_score,
        )

        diagnosis = self._build_diagnosis(metrics)
        pipeline_steps = self._ops_to_display(plan.operations)

        return {
            "resolution": {"width": w, "height": h},
            "metrics": metrics.to_dict(),
            "overall_quality": round(metrics.overall_quality, 1),
            "quality_label": (
                "POOR" if metrics.overall_quality < 35
                else "DEGRADED" if metrics.overall_quality < 65
                else "ACCEPTABLE" if metrics.overall_quality < 82
                else "GOOD"
            ),
            "diagnosis": diagnosis,
            "should_enhance": plan.should_enhance,
            "enhancement_level": plan.enhancement_level,
            "recommended_pipeline": pipeline_steps,
            "assessor_diagnosis": plan.assessor_diagnosis,
        }

    def run(
        self,
        image_bytes: bytes,
        operations_override: Optional[List[str]] = None,
        enhancement_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the enhancement pipeline on an image.
        Returns the enhanced image as base64, quality before/after, and metadata.
        """
        t0 = time.perf_counter()

        frame = self._decode_image(image_bytes)
        if frame is None:
            return {"error": "Could not decode image. Ensure it is a valid JPEG/PNG file."}

        h, w = frame.shape[:2]

        # 1. Analyze quality before
        metrics_before = self.analyzer.analyze(frame)
        is_blurry = metrics_before.blur_score < 100.0

        # 2. Build plan
        level_upper = (enhancement_level or "").strip().upper()
        if operations_override:
            plan = EnhancementPlan(
                should_enhance=True,
                enhancement_level="manual",
                operations=operations_override,
                assessor_diagnosis="Manual operation override by operator.",
            )
        elif level_upper == "LIGHT":
            plan = EnhancementPlan(
                should_enhance=True,
                enhancement_level="light",
                operations=["adaptive_clahe", "adaptive_sharpening"],
                assessor_diagnosis="Operator selected LIGHT enhancement profile.",
            )
        elif level_upper == "MODERATE":
            plan = EnhancementPlan(
                should_enhance=True,
                enhancement_level="moderate",
                operations=["adaptive_clahe", "fast_denoising", "adaptive_sharpening"],
                assessor_diagnosis="Operator selected MODERATE enhancement profile.",
            )
        elif level_upper == "AGGRESSIVE":
            plan = EnhancementPlan(
                should_enhance=True,
                enhancement_level="aggressive",
                operations=["adaptive_gamma", "shadow_recovery", "adaptive_clahe", "fast_denoising", "unsharp_masking"],
                assessor_diagnosis="Operator selected AGGRESSIVE enhancement profile.",
            )
        else:
            plan = self.decision_engine.create_plan_from_quality(
                metrics=metrics_before,
                is_blurry_from_assessor=is_blurry,
                blur_score_from_assessor=metrics_before.blur_score,
            )

        # 3. Execute enhancement
        if plan.should_enhance:
            enhanced = self.processor.execute_plan(frame, plan)
        else:
            enhanced = frame.copy()

        # 4. Analyze quality after
        metrics_after = self.analyzer.analyze(enhanced)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # 5. Encode results
        original_bytes = self._encode_image(frame)
        enhanced_bytes = self._encode_image(enhanced)

        original_b64 = base64.b64encode(original_bytes).decode("utf-8")
        enhanced_b64 = base64.b64encode(enhanced_bytes).decode("utf-8")

        # 6. Integrity hashes
        original_hash = self._sha256(original_bytes)
        enhanced_hash = self._sha256(enhanced_bytes)

        # 7. Persist to disk for evidence verification
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        enhanced_dir = os.path.join(base_dir, "data", "enhanced")
        originals_dir = os.path.join(base_dir, "data", "originals")
        os.makedirs(enhanced_dir, exist_ok=True)
        os.makedirs(originals_dir, exist_ok=True)

        orig_filepath = os.path.join(originals_dir, f"{original_hash}.jpg")
        enh_filepath = os.path.join(enhanced_dir, f"{enhanced_hash}.jpg")

        with open(orig_filepath, "wb") as f:
            f.write(original_bytes)
        with open(enh_filepath, "wb") as f:
            f.write(enhanced_bytes)

        response_data = {
            "status": "enhanced" if plan.should_enhance else "unchanged",
            "source": {
                "resolution": {"width": w, "height": h},
                "quality_score": round(metrics_before.overall_quality, 1),
                "metrics": metrics_before.to_dict(),
                "image_b64": original_b64,
                "integrity_hash": original_hash,
                "file_path": orig_filepath,
                "file_exists": os.path.exists(orig_filepath),
            },
            "output": {
                "resolution": {"width": enhanced.shape[1], "height": enhanced.shape[0]},
                "quality_score": round(metrics_after.overall_quality, 1),
                "metrics": metrics_after.to_dict(),
                "image_b64": enhanced_b64,
                "integrity_hash": enhanced_hash,
                "file_path": enh_filepath,
                "file_exists": os.path.exists(enh_filepath),
            },
            "validation": {
                "before_hash": original_hash,
                "after_hash": enhanced_hash,
                "source_hash": original_hash,
                "output_hash": enhanced_hash,
                "hash_changed": (original_hash != enhanced_hash),
                "file_on_disk": os.path.exists(enh_filepath),
                "saved_to_disk": os.path.exists(enh_filepath),
                "derivative_path": enh_filepath,
                "legal_notice": "Internal Verification Hash · Non-Certified Operational Preview",
            },
            "processing": {
                "enhancement_level": plan.enhancement_level,
                "level": plan.enhancement_level,
                "operations_applied": plan.operations,
                "pipeline_display": self._ops_to_display(plan.operations),
                "pipeline_steps": self._ops_to_display(plan.operations),
                "processing_time_ms": round(elapsed_ms, 1),
                "engine": "ForensicProcessor (classical CV)",
                "device": "CPU",
                "should_enhance": plan.should_enhance,
            },
        }

        # Persist operational processing metadata to repository
        try:
            self.repository.save_enhancement_metadata({
                "derivative_hash": enhanced_hash,
                "source_hash": original_hash,
                "source_path": orig_filepath,
                "derivative_path": enh_filepath,
                "operations_applied": plan.operations,
                "processing_time_ms": round(elapsed_ms, 1),
                "engine": "ForensicProcessor (classical CV)",
                "quality_before": round(metrics_before.overall_quality, 1),
                "quality_after": round(metrics_after.overall_quality, 1),
            })
        except Exception:
            pass

        return response_data

    def status(self) -> Dict[str, Any]:
        """Return the readiness status of the enhancement engine."""
        return {
            "ready": self._ready,
            "status": "ready" if self._ready else "unavailable",
            "engine": "ForensicProcessor",
            "implementation": "classical-cv",
            "operations_available": [
                "adaptive_gamma", "shadow_recovery", "exposure_correction",
                "highlight_recovery", "adaptive_clahe", "contrast_stretching",
                "color_constancy", "fast_denoising", "edge_preserving_filter",
                "deblurring", "unsharp_masking", "adaptive_sharpening",
            ],
        }
