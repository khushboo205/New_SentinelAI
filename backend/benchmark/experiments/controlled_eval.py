"""
SentinelAI Benchmark — Experiment 2: Controlled Ground-Truth Reference Evaluation

Evaluates synthetic degradations with a known clean reference:
- Computes Full-Reference Metrics: PSNR (dB), SSIM, MSE against clean reference
- Computes No-Reference Metrics across Clean, Degraded, and Enhanced
- Evaluates Downstream EasyOCR character accuracy against known ground truth
- Measures execution latencies and SHA-256 file digests
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np

from benchmark.metrics.image_quality import (
    calculate_full_reference_metrics,
    calculate_no_reference_metrics,
)
from benchmark.metrics.downstream import compare_ocr_extraction
from services.enhancer import Enhancer
from services.model_manager import ModelManager


def run_controlled_reference_experiment(
    output_derivative_dir: Path,
    enhancement_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Run controlled reference experiment with synthetic degradation and ground truth verification.
    """
    output_derivative_dir.mkdir(parents=True, exist_ok=True)
    enhancer = Enhancer()
    mm = ModelManager()
    ocr_reader = mm.load_ocr()

    # 1. Generate High-Quality Ground-Truth Reference (Synthetic Border License Plate Scene)
    ref_w, ref_h = 420, 140
    ref_img = np.full((ref_h, ref_w, 3), 235, dtype=np.uint8)
    
    # Border & Tactical Metadata
    cv2.rectangle(ref_img, (8, 8), (ref_w - 8, ref_h - 8), (30, 30, 30), 2)
    cv2.rectangle(ref_img, (16, 16), (65, ref_h - 16), (180, 50, 20), -1)
    cv2.putText(ref_img, "IN", (24, 78), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    # Ground Truth Plate String
    ground_truth_text = "DL-01-CV-2026"
    cv2.putText(ref_img, ground_truth_text, (80, 85), cv2.FONT_HERSHEY_SIMPLEX, 1.35, (15, 15, 15), 3)

    ref_bytes = cv2.imencode(".png", ref_img)[1].tobytes()
    ref_hash = hashlib.sha256(ref_bytes).hexdigest()
    ref_file = output_derivative_dir / "controlled_clean_reference.png"
    ref_file.write_bytes(ref_bytes)

    # 2. Synthesize Real-World CCTV Degradation:
    # A) Severe Underexposure (factor 0.30 -> low-light night conditions)
    # B) Optical Gaussian Blur (kernel 5x5, sigma 1.8)
    # C) Additive Zero-Mean Sensor Noise (std dev 12)
    np.random.seed(42)  # Fixed seed for strict mathematical reproducibility
    degraded = (ref_img.astype(np.float32) * 0.30)
    degraded = cv2.GaussianBlur(degraded, (5, 5), 1.8)
    noise = np.random.normal(0, 12, degraded.shape).astype(np.float32)
    degraded = np.clip(degraded + noise, 0, 255).astype(np.uint8)

    deg_bytes = cv2.imencode(".png", degraded)[1].tobytes()
    deg_hash = hashlib.sha256(deg_bytes).hexdigest()
    deg_file = output_derivative_dir / "controlled_degraded_input.png"
    deg_file.write_bytes(deg_bytes)

    # 3. Apply SentinelAI Forensic Enhancement
    t0_enh = time.perf_counter()
    enhanced = enhancer.enhance(degraded, level=enhancement_level)
    enh_latency_ms = (time.perf_counter() - t0_enh) * 1000.0

    enh_bytes = cv2.imencode(".png", enhanced)[1].tobytes()
    enh_hash = hashlib.sha256(enh_bytes).hexdigest()
    enh_file = output_derivative_dir / "controlled_enhanced_output.png"
    enh_file.write_bytes(enh_bytes)

    # 4. Compute Full-Reference Metrics (Against Clean Reference)
    ref_metrics_deg = calculate_full_reference_metrics(target=degraded, reference=ref_img)
    ref_metrics_enh = calculate_full_reference_metrics(target=enhanced, reference=ref_img)

    # 5. Compute No-Reference Metrics
    no_ref_clean = calculate_no_reference_metrics(ref_img)
    no_ref_deg = calculate_no_reference_metrics(degraded)
    no_ref_enh = calculate_no_reference_metrics(enhanced)

    # 6. Downstream EasyOCR Extraction
    ocr_comparison = compare_ocr_extraction(
        reader=ocr_reader,
        img_orig=degraded,
        img_enh=enhanced,
        ground_truth=ground_truth_text
    )

    return {
        "experiment_name": "Controlled Reference Ground-Truth Benchmark",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "ground_truth_text": ground_truth_text,
        "files": {
            "clean_reference": {"path": str(ref_file), "sha256": ref_hash},
            "degraded_input": {"path": str(deg_file), "sha256": deg_hash},
            "enhanced_output": {"path": str(enh_file), "sha256": enh_hash},
            "hashes_distinct": (ref_hash != deg_hash != enh_hash)
        },
        "enhancement_latency_ms": round(enh_latency_ms, 2),
        "full_reference_metrics": {
            "degraded_vs_clean": ref_metrics_deg,
            "enhanced_vs_clean": ref_metrics_enh,
            "psnr_gain_db": round(ref_metrics_enh["psnr_db"] - ref_metrics_deg["psnr_db"], 2),
            "ssim_gain": round((ref_metrics_enh["ssim"] or 0.0) - (ref_metrics_deg["ssim"] or 0.0), 4),
            "mse_reduction": round(ref_metrics_deg["mse"] - ref_metrics_enh["mse"], 2),
            "mse_delta": round(ref_metrics_enh["mse"] - ref_metrics_deg["mse"], 2)
        },
        "no_reference_metrics": {
            "clean": no_ref_clean,
            "degraded": no_ref_deg,
            "enhanced": no_ref_enh
        },
        "downstream_ocr": ocr_comparison
    }
