"""
SentinelAI Benchmark Suite — Downstream Analytics Comparators

Evaluates how adaptive forensic enhancement influences downstream AI models:
1. YOLO11 Object Detection:
   - Detection count comparison
   - Mean & per-class confidence shifts
   - IoU-matched detection tracking
   - Latency & FPS profiling
2. EasyOCR / ANPR:
   - Text extraction accuracy
   - OCR confidence shifts
   - Character error rate (when ground truth is available)
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np


def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Compute Intersection over Union (IoU) between two [x1, y1, x2, y2] boxes."""
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])

    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h

    area1 = max(0.0, (box1[2] - box1[0]) * (box1[3] - box1[1]))
    area2 = max(0.0, (box2[2] - box2[0]) * (box2[3] - box2[1]))
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area / union_area)


def compare_yolo_detections(
    model: Any,
    img_orig: np.ndarray,
    img_enh: np.ndarray,
    conf_threshold: float = 0.25,
    iou_match_threshold: float = 0.45
) -> Dict[str, Any]:
    """
    Run real YOLO inference on original vs enhanced images and measure differences.

    SCIENTIFIC METHODOLOGY NOTE:
    - Model Warm-Up: Timings represent steady-state inference latency when preceded by
      an explicit warm-up inference (isolating PyTorch weight-loading and JIT compilation).
    - Condition-Dependent Response: Field CCTV frames lack ground-truth object annotations.
      Therefore, changes in detection count and confidence measure condition-dependent
      model response to contrast and spatial gradient changes, NOT validated detection accuracy
      or mAP improvements.
    - Matching Criterion: Detections between original and enhanced frames are paired if
      class labels match and IoU >= iou_match_threshold (default 0.45).

    Parameters:
        model: Ultralytics YOLO instance
        img_orig: Original CCTV image (BGR)
        img_enh: Enhanced derivative image (BGR)
        conf_threshold: Minimum detection confidence
        iou_match_threshold: IoU threshold for matching corresponding objects

    Returns:
        Structured dictionary comparing detections, confidences, and latencies.
    """
    # 1. Infer Original
    t0 = time.perf_counter()
    preds_orig = model.predict(source=img_orig, conf=conf_threshold, verbose=False)
    lat_orig_ms = (time.perf_counter() - t0) * 1000.0

    # 2. Infer Enhanced
    t0 = time.perf_counter()
    preds_enh = model.predict(source=img_enh, conf=conf_threshold, verbose=False)
    lat_enh_ms = (time.perf_counter() - t0) * 1000.0

    # Parse Original Detections
    dets_orig = []
    for b in preds_orig[0].boxes:
        c_id = int(b.cls[0])
        c_name = model.names[c_id]
        conf = float(b.conf[0])
        box = [float(x) for x in b.xyxy[0].tolist()]
        dets_orig.append({
            "class_id": c_id,
            "class_name": c_name,
            "confidence": round(conf, 4),
            "bbox": [round(x, 1) for x in box]
        })

    # Parse Enhanced Detections
    dets_enh = []
    for b in preds_enh[0].boxes:
        c_id = int(b.cls[0])
        c_name = model.names[c_id]
        conf = float(b.conf[0])
        box = [float(x) for x in b.xyxy[0].tolist()]
        dets_enh.append({
            "class_id": c_id,
            "class_name": c_name,
            "confidence": round(conf, 4),
            "bbox": [round(x, 1) for x in box]
        })

    # Summary Statistics
    count_orig = len(dets_orig)
    count_enh = len(dets_enh)

    confs_orig = [d["confidence"] for d in dets_orig]
    confs_enh = [d["confidence"] for d in dets_enh]

    mean_conf_orig = float(np.mean(confs_orig)) if confs_orig else 0.0
    mean_conf_enh = float(np.mean(confs_enh)) if confs_enh else 0.0
    conf_delta = round(mean_conf_enh - mean_conf_orig, 4)

    # Correlate matched detections via IoU
    matched_pairs = []
    unmatched_orig = list(range(len(dets_orig)))
    unmatched_enh = list(range(len(dets_enh)))

    for i, d_orig in enumerate(dets_orig):
        best_iou = 0.0
        best_j = -1
        for j in unmatched_enh:
            d_enh = dets_enh[j]
            if d_orig["class_name"] == d_enh["class_name"]:
                iou = compute_iou(d_orig["bbox"], d_enh["bbox"])
                if iou > best_iou and iou >= iou_match_threshold:
                    best_iou = iou
                    best_j = j
        if best_j != -1:
            unmatched_orig.remove(i)
            unmatched_enh.remove(best_j)
            matched_pairs.append({
                "class_name": d_orig["class_name"],
                "iou": round(best_iou, 3),
                "conf_orig": d_orig["confidence"],
                "conf_enh": dets_enh[best_j]["confidence"],
                "conf_gain": round(dets_enh[best_j]["confidence"] - d_orig["confidence"], 4)
            })

    return {
        "count_orig": count_orig,
        "count_enh": count_enh,
        "count_delta": count_enh - count_orig,
        "mean_confidence_orig": round(mean_conf_orig, 4),
        "mean_confidence_enh": round(mean_conf_enh, 4),
        "mean_confidence_delta": conf_delta,
        "latency_orig_ms": round(lat_orig_ms, 2),
        "latency_enh_ms": round(lat_enh_ms, 2),
        "fps_orig": round(1000.0 / max(1.0, lat_orig_ms), 1),
        "fps_enh": round(1000.0 / max(1.0, lat_enh_ms), 1),
        "matched_detections_count": len(matched_pairs),
        "matched_pairs": matched_pairs,
        "newly_detected_count": len(unmatched_enh),
        "dropped_detections_count": len(unmatched_orig),
        "detections_orig": dets_orig,
        "detections_enh": dets_enh,
    }


def compare_ocr_extraction(
    reader: Any,
    img_orig: np.ndarray,
    img_enh: np.ndarray,
    ground_truth: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run real EasyOCR inference on original vs enhanced text/plate crops.

    SCIENTIFIC NOTE:
    - OCR Confidence vs Character Accuracy: OCR confidence is the model's internal softmax
      probability for detected text tokens. Character accuracy is the objective Levenshtein-distance-based
      fidelity against verified ground-truth text:
        Accuracy = max(0.0, 1.0 - (Levenshtein_Distance(pred, GT) / len(GT)))
    - Changes in confidence do not necessarily correlate with accuracy changes; when character accuracy
      is identical, an increase or decrease in confidence must be reported as a confidence shift,
      not an accuracy improvement.

    Parameters:
        reader: EasyOCR Reader instance
        img_orig: Original crop (BGR)
        img_enh: Enhanced crop (BGR)
        ground_truth: Optional true expected text string

    Returns:
        Structured dictionary comparing OCR outputs, confidences, and edit distances.
    """
    # 1. Read Original
    t0 = time.perf_counter()
    res_orig = reader.readtext(img_orig)
    lat_orig_ms = (time.perf_counter() - t0) * 1000.0

    # 2. Read Enhanced
    t0 = time.perf_counter()
    res_enh = reader.readtext(img_enh)
    lat_enh_ms = (time.perf_counter() - t0) * 1000.0

    parsed_orig = [{"text": r[1], "confidence": round(float(r[2]), 4)} for r in res_orig]
    parsed_enh = [{"text": r[1], "confidence": round(float(r[2]), 4)} for r in res_enh]

    combined_text_orig = " ".join([r["text"] for r in parsed_orig]).strip()
    combined_text_enh = " ".join([r["text"] for r in parsed_enh]).strip()

    confs_orig = [r["confidence"] for r in parsed_orig]
    confs_enh = [r["confidence"] for r in parsed_enh]

    mean_conf_orig = float(np.mean(confs_orig)) if confs_orig else 0.0
    mean_conf_enh = float(np.mean(confs_enh)) if confs_enh else 0.0

    comparison: Dict[str, Any] = {
        "text_orig": combined_text_orig,
        "text_enh": combined_text_enh,
        "words_detected_orig": len(parsed_orig),
        "words_detected_enh": len(parsed_enh),
        "mean_conf_orig": round(mean_conf_orig, 4),
        "mean_conf_enh": round(mean_conf_enh, 4),
        "conf_delta": round(mean_conf_enh - mean_conf_orig, 4),
        "latency_orig_ms": round(lat_orig_ms, 2),
        "latency_enh_ms": round(lat_enh_ms, 2),
        "raw_results_orig": parsed_orig,
        "raw_results_enh": parsed_enh,
    }

    if ground_truth:
        comparison["ground_truth"] = ground_truth
        clean_gt = ground_truth.upper().replace(" ", "").replace("-", "")
        clean_o = combined_text_orig.upper().replace(" ", "").replace("-", "")
        clean_e = combined_text_enh.upper().replace(" ", "").replace("-", "")

        comparison["exact_match_orig"] = (clean_o == clean_gt)
        comparison["exact_match_enh"] = (clean_e == clean_gt)

        # Simple Levenshtein distance for character error rate
        def levenshtein(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                curr = [i + 1]
                for j, c2 in enumerate(s2):
                    ins = prev[j + 1] + 1
                    dels = curr[j] + 1
                    subs = prev[j] + (c1 != c2)
                    curr.append(min(ins, dels, subs))
                prev = curr
            return prev[-1]

        dist_orig = levenshtein(clean_o, clean_gt)
        dist_enh = levenshtein(clean_e, clean_gt)
        comparison["edit_distance_orig"] = dist_orig
        comparison["edit_distance_enh"] = dist_enh
        comparison["char_accuracy_orig"] = round(max(0.0, 1.0 - (dist_orig / max(1, len(clean_gt)))), 4)
        comparison["char_accuracy_enh"] = round(max(0.0, 1.0 - (dist_enh / max(1, len(clean_gt)))), 4)

    return comparison
