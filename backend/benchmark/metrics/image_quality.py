"""
SentinelAI Benchmark Suite — Image Quality Metrics

Provides rigorous computation of:
1. No-Reference Quality Metrics:
   - Laplacian blur variance
   - Tenengrad sharpness gradient
   - Mean luminance (brightness)
   - RMS contrast
   - Dynamic range (p95 - p5)
   - Noise floor standard deviation
   - Shannon entropy
2. Full-Reference Fidelity Metrics (when reference image exists):
   - Peak Signal-to-Noise Ratio (PSNR)
   - Structural Similarity Index (SSIM)
   - Mean Squared Error (MSE)
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np

try:
    from skimage.metrics import peak_signal_noise_ratio as compute_psnr
    from skimage.metrics import structural_similarity as compute_ssim
    SKIMAGE_AVAILABLE = True
except ImportError:
    compute_psnr = None
    compute_ssim = None
    SKIMAGE_AVAILABLE = False


def calculate_no_reference_metrics(image: np.ndarray) -> Dict[str, float]:
    """
    Calculate objective, reproducible no-reference quality metrics on an image.

    SCIENTIFIC NOTE:
    - Laplacian variance and Tenengrad sharpness quantify high-frequency spatial gradients
      and edge energy. They MUST NOT be interpreted as a direct percentage reduction in optical blur,
      because unsharp filtering and noise amplification naturally elevate high-frequency variance.
    - Noise standard deviation (noise_std) measures residual high-frequency fluctuations after
      median filtering. Enhancement filters often elevate noise residuals.
    - No synthetic composite "quality score" is computed to avoid unscientific aggregation.

    Parameters:
        image: BGR or Grayscale uint8 numpy array.

    Returns:
        Dictionary containing quantitative metrics.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot calculate metrics on None or empty image.")

    if len(image.shape) == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 1. Laplacian Blur Variance: sigma^2(grad^2(I)) - high-frequency edge gradient indicator
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_score = float(laplacian.var())

    # 2. Tenengrad Sharpness: mean of gradient magnitude sqrt(Gx^2 + Gy^2) - gradient energy indicator
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = float(np.mean(np.sqrt(gx**2 + gy**2)))

    # 3. Mean Luminance / Brightness (0 - 255)
    brightness = float(np.mean(gray))

    # 4. RMS Contrast: standard deviation of luminance intensities
    contrast = float(np.std(gray))

    # 5. Dynamic Range: span between 95th and 5th percentiles
    p5, p95 = np.percentile(gray, [5, 95])
    dynamic_range = float(p95 - p5)

    # 6. Noise Floor Estimate: std dev of residual after 3x3 median filtering
    median_filtered = cv2.medianBlur(gray, 3)
    noise_estimate = float(np.std(gray.astype(np.float32) - median_filtered.astype(np.float32)))

    # 7. Shannon Entropy: measure of information content / grayscale diversity
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_norm = hist.ravel() / max(1.0, float(hist.sum()))
    hist_nonzero = hist_norm[hist_norm > 0]
    shannon_entropy = float(-np.sum(hist_nonzero * np.log2(hist_nonzero)))

    return {
        "blur_laplacian": round(blur_score, 2),
        "sharpness_tenengrad": round(tenengrad, 2),
        "brightness_mean": round(brightness, 2),
        "contrast_rms": round(contrast, 2),
        "dynamic_range": round(dynamic_range, 2),
        "noise_std": round(noise_estimate, 2),
        "shannon_entropy": round(shannon_entropy, 4),
    }


def calculate_full_reference_metrics(
    target: np.ndarray,
    reference: np.ndarray
) -> Dict[str, Optional[float]]:
    """
    Calculate full-reference fidelity metrics between a target image and a ground-truth reference.

    SCIENTIFIC NOTE:
    PSNR and SSIM are only mathematically and conceptually meaningful when comparing
    an image against an authentic clean reference (e.g. in synthetic degradation tests).
    Measuring PSNR between a degraded CCTV image and an enhanced image measures mathematical
    divergence, NOT restoration accuracy.
    - MSE (Mean Squared Error): Pixel error metric where LOWER is better.
    - PSNR (Peak Signal-to-Noise Ratio): Logarithmic ratio where HIGHER is better.
    - SSIM (Structural Similarity Index): Structural preservation metric where HIGHER is better.
    - Note: Higher PSNR does NOT imply universal restoration success, as SSIM can decline
      if unsharp edge enhancement introduces structural overshoot.

    Parameters:
        target: Target BGR or Grayscale uint8 numpy array.
        reference: Reference BGR or Grayscale uint8 numpy array of identical dimensions.

    Returns:
        Dictionary containing PSNR, SSIM, MSE, or informative error indicators.
    """
    if target is None or reference is None:
        raise ValueError("Both target and reference must be valid numpy arrays.")

    if target.shape != reference.shape:
        raise ValueError(
            f"Shape mismatch: target {target.shape} vs reference {reference.shape}. "
            "Full-reference metrics require identical resolution and channel count."
        )

    # Convert to grayscale for consistent luminance structural comparison
    if len(target.shape) == 3 and target.shape[2] == 3:
        t_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        r_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    else:
        t_gray = target
        r_gray = reference

    # Mean Squared Error (MSE)
    mse = float(np.mean((t_gray.astype(np.float64) - r_gray.astype(np.float64)) ** 2))

    if not SKIMAGE_AVAILABLE:
        # Fallback manual PSNR calculation
        if mse == 0:
            psnr = float("inf")
        else:
            psnr = float(10 * math.log10((255.0 ** 2) / mse))
        ssim = None
    else:
        psnr = float(compute_psnr(r_gray, t_gray, data_range=255))
        ssim = float(compute_ssim(r_gray, t_gray, data_range=255))

    return {
        "mse": round(mse, 3),
        "psnr_db": round(psnr, 2) if not math.isinf(psnr) else 999.0,
        "ssim": round(ssim, 4) if ssim is not None else None,
        "lpips": None,  # lpips package is not installed; documented in benchmark methodology
    }
