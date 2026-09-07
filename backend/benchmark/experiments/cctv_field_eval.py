"""
SentinelAI Benchmark — Experiment 1: Real-World Degraded CCTV Field Evaluation

Evaluates actual CCTV surveillance frames without synthetic degradation:
- Compares Original CCTV vs SentinelAI Enhanced CCTV
- Measures No-Reference Physical Quality Metrics (Sharpness, Contrast, Luminance, Noise)
- Measures Downstream YOLO11 Detections & Confidence
- Non-destructively saves derivatives and verifies SHA-256 cryptographic integrity
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np

from benchmark.metrics.image_quality import calculate_no_reference_metrics
from benchmark.metrics.downstream import compare_yolo_detections
from services.enhancer import Enhancer
from ultralytics import YOLO


def run_cctv_field_experiment(
    sample_paths: List[Path],
    output_derivative_dir: Path,
    yolo_model_path: Path,
    enhancement_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Run complete no-reference field evaluation across real CCTV samples.
    """
    output_derivative_dir.mkdir(parents=True, exist_ok=True)
    enhancer = Enhancer()
    yolo_model = YOLO(str(yolo_model_path))

    # Explicit YOLO model warm-up: isolates cold-start / PyTorch weight loading & JIT
    # from steady-state inference latency measurements across field samples.
    dummy_input = np.zeros((640, 640, 3), dtype=np.uint8)
    t0_warmup = time.perf_counter()
    _ = yolo_model.predict(source=dummy_input, conf=0.25, verbose=False)
    cold_start_latency_ms = round((time.perf_counter() - t0_warmup) * 1000.0, 2)

    results: List[Dict[str, Any]] = []
    total_t0 = time.perf_counter()

    for path in sample_paths:
        if not path.exists():
            continue

        raw_bytes = path.read_bytes()
        orig_hash = hashlib.sha256(raw_bytes).hexdigest()

        img_orig = cv2.imread(str(path))
        if img_orig is None:
            continue

        # 1. No-Reference Quality (Original)
        q_orig = calculate_no_reference_metrics(img_orig)

        # 2. Enhancement Timing & Execution
        t0_enh = time.perf_counter()
        img_enh = enhancer.enhance(img_orig, level=enhancement_level)
        t_enh_ms = (time.perf_counter() - t0_enh) * 1000.0

        # 3. No-Reference Quality (Enhanced)
        q_enh = calculate_no_reference_metrics(img_enh)

        # 4. Encode & Save Derivative
        success, enh_buf = cv2.imencode(".jpg", img_enh, [cv2.IMWRITE_JPEG_QUALITY, 92])
        if not success:
            continue
        enh_bytes = enh_buf.tobytes()
        enh_hash = hashlib.sha256(enh_bytes).hexdigest()

        derivative_path = output_derivative_dir / f"{path.stem}_enhanced_{enh_hash[:10]}.jpg"
        derivative_path.write_bytes(enh_bytes)

        # 5. Downstream YOLO11 Inference Comparison
        downstream_yolo = compare_yolo_detections(
            model=yolo_model,
            img_orig=img_orig,
            img_enh=img_enh,
            conf_threshold=0.25
        )

        sample_record = {
            "sample_name": path.name,
            "source_path": str(path),
            "source_resolution": [img_orig.shape[1], img_orig.shape[0]],
            "source_sha256": orig_hash,
            "derivative_path": str(derivative_path),
            "derivative_sha256": enh_hash,
            "sha256_distinct": (orig_hash != enh_hash),
            "source_unmodified": (hashlib.sha256(path.read_bytes()).hexdigest() == orig_hash),
            "enhancement_level": enhancement_level,
            "enhancement_latency_ms": round(t_enh_ms, 2),
            "quality_metrics": {
                "original": q_orig,
                "enhanced": q_enh,
                "delta": {
                    "blur_laplacian": round(q_enh["blur_laplacian"] - q_orig["blur_laplacian"], 2),
                    "sharpness_tenengrad": round(q_enh["sharpness_tenengrad"] - q_orig["sharpness_tenengrad"], 2),
                    "brightness_mean": round(q_enh["brightness_mean"] - q_orig["brightness_mean"], 2),
                    "contrast_rms": round(q_enh["contrast_rms"] - q_orig["contrast_rms"], 2),
                    "dynamic_range": round(q_enh["dynamic_range"] - q_orig["dynamic_range"], 2),
                    "noise_std": round(q_enh["noise_std"] - q_orig["noise_std"], 2),
                    "shannon_entropy": round(q_enh["shannon_entropy"] - q_orig["shannon_entropy"], 4),
                }
            },
            "downstream_yolo": downstream_yolo
        }
        results.append(sample_record)

    total_latency_ms = (time.perf_counter() - total_t0) * 1000.0

    return {
        "experiment_name": "Real-World Degraded CCTV Field Evaluation",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "samples_evaluated_count": len(results),
        "total_latency_ms": round(total_latency_ms, 2),
        "enhancement_profile": enhancement_level,
        "yolo_model": yolo_model_path.name,
        "yolo_warmup_performed": True,
        "yolo_cold_start_latency_ms": cold_start_latency_ms,
        "samples": results
    }
