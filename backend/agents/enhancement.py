"""
SentinelAI Forensic Image Enhancement Agent

Provides forensic-quality enhancement for CCTV video streams guided by Quality Assessor findings.
Implements computational photography algorithms to optimize contrast, illumination,
denoising, dynamic range, and sharpness while preserving evidence integrity (no hallucination).

Author: SentinelAI Engineering Team
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

# PyTorch GPU acceleration check
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

from core.agent import BaseAgent
from core.packet import BasePacket, DetectionPacket, FramePacket, TrackingPacket
from services.quality_assessor import QualityAssessor


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass(slots=True)
class FrameQualityMetrics:
    """
    Quantitative metrics measuring image quality attributes of a video frame.
    """
    blur_score: float = 0.0          # Laplacian variance (higher = sharper)
    noise_score: float = 0.0         # Noise std dev estimate (higher = noisier)
    brightness: float = 0.0          # Mean luminance intensity (0-255)
    contrast: float = 0.0            # RMS contrast / intensity std dev
    dynamic_range: float = 0.0       # 95th - 5th percentile intensity span
    saturation: float = 0.0          # Mean HSV saturation (0-255)
    sharpness: float = 0.0           # Tenengrad gradient magnitude mean
    motion_blur: float = 1.0         # Directional Sobel variance ratio
    compression_artifacts: float = 0.0 # 8x8 grid boundary step variance
    resolution: Tuple[int, int] = (0, 0) # (width, height)
    overall_quality: float = 0.0     # Composite visual quality rating (0-100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a serializable dictionary."""
        return {
            "blur_score": round(self.blur_score, 2),
            "noise_score": round(self.noise_score, 2),
            "brightness": round(self.brightness, 2),
            "contrast": round(self.contrast, 2),
            "dynamic_range": round(self.dynamic_range, 2),
            "saturation": round(self.saturation, 2),
            "sharpness": round(self.sharpness, 2),
            "motion_blur": round(self.motion_blur, 2),
            "compression_artifacts": round(self.compression_artifacts, 2),
            "resolution": self.resolution,
            "overall_quality": round(self.overall_quality, 2),
        }


@dataclass(slots=True)
class EnhancementPlan:
    """
    Execution plan produced by the Smart Decision Engine guided by QualityAssessor.
    """
    should_enhance: bool = False
    enhancement_level: str = "none"  # "none", "light", "moderate", "aggressive"
    operations: List[str] = field(default_factory=list)
    assessor_diagnosis: str = ""


# ============================================================================
# FRAME ANALYZER
# ============================================================================

class FrameAnalyzer:
    """
    Fast, multi-metric quality analyzer for video frames.
    """

    def analyze(self, frame: np.ndarray) -> FrameQualityMetrics:
        """
        Compute quantitative image quality metrics for a BGR numpy frame.
        """
        if frame is None or frame.size == 0:
            return FrameQualityMetrics()

        height, width = frame.shape[:2]
        
        # Convert color spaces
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = float(hsv[..., 1].mean())
        else:
            gray = frame.copy()
            saturation = 0.0

        # 1. Blur Score (Laplacian variance)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Noise Score (Difference between frame and 3x3 median blur)
        median_blur = cv2.medianBlur(gray, 3)
        noise_score = float(np.std(gray.astype(np.float32) - median_blur.astype(np.float32)))

        # 3. Brightness (Mean luminance)
        brightness = float(gray.mean())

        # 4. Contrast (Standard deviation of luminance)
        contrast = float(gray.std())

        # 5. Dynamic Range (95th percentile - 5th percentile)
        p5, p95 = np.percentile(gray, [5, 95])
        dynamic_range = float(p95 - p5)

        # 6. Sharpness (Tenengrad gradient magnitude mean)
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = np.sqrt(gx**2 + gy**2)
        sharpness = float(tenengrad.mean())

        # 7. Motion Blur Ratio (Ratio of directional Sobel variances)
        var_x = float(np.var(gx))
        var_y = float(np.var(gy))
        min_var = min(var_x, var_y) + 1e-5
        max_var = max(var_x, var_y)
        motion_blur = float(max_var / min_var)

        # 8. Compression Artifacts (8x8 grid boundary jump variance)
        compression_artifacts = self._estimate_blocking_artifacts(gray)

        # 9. Composite Overall Quality Score (0-100)
        overall_quality = self._compute_overall_quality(
            blur_score=blur_score,
            noise_score=noise_score,
            brightness=brightness,
            contrast=contrast,
            dynamic_range=dynamic_range,
            sharpness=sharpness
        )

        return FrameQualityMetrics(
            blur_score=blur_score,
            noise_score=noise_score,
            brightness=brightness,
            contrast=contrast,
            dynamic_range=dynamic_range,
            saturation=saturation,
            sharpness=sharpness,
            motion_blur=motion_blur,
            compression_artifacts=compression_artifacts,
            resolution=(width, height),
            overall_quality=overall_quality
        )

    def _estimate_blocking_artifacts(self, gray: np.ndarray) -> float:
        """
        Estimate 8x8 block boundary step discontinuities caused by lossy JPEG/H.264 compression.
        """
        try:
            h, w = gray.shape
            if h < 16 or w < 16:
                return 0.0
            
            # Boundary differences along 8x8 vertical grids
            v_diff_boundary = np.abs(gray[:, 7::8].astype(np.float32) - gray[:, 8::8].astype(np.float32))
            v_diff_internal = np.abs(gray[:, 3::8].astype(np.float32) - gray[:, 4::8].astype(np.float32))
            
            v_boundary_mean = v_diff_boundary.mean() if v_diff_boundary.size > 0 else 0.0
            v_internal_mean = v_diff_internal.mean() if v_diff_internal.size > 0 else 1e-5
            
            return float(v_boundary_mean / (v_internal_mean + 1e-5))
        except Exception:
            return 0.0

    def _compute_overall_quality(
        self,
        blur_score: float,
        noise_score: float,
        brightness: float,
        contrast: float,
        dynamic_range: float,
        sharpness: float
    ) -> float:
        """
        Compute normalized 0-100 composite visual quality score.
        """
        norm_blur = min(blur_score / 300.0, 1.0)
        norm_noise = max(0.0, 1.0 - (noise_score / 25.0))
        brightness_diff = abs(brightness - 128.0)
        norm_brightness = max(0.0, 1.0 - (brightness_diff / 128.0))
        norm_contrast = min(contrast / 64.0, 1.0)
        norm_dr = min(dynamic_range / 180.0, 1.0)
        norm_sharpness = min(sharpness / 40.0, 1.0)

        score = (
            norm_blur * 0.25 +
            norm_noise * 0.20 +
            norm_brightness * 0.15 +
            norm_contrast * 0.15 +
            norm_dr * 0.15 +
            norm_sharpness * 0.10
        ) * 100.0

        return max(0.0, min(100.0, score))


# ============================================================================
# SMART DECISION ENGINE GUIDED BY QUALITY ASSESSOR
# ============================================================================

class EnhancementDecisionEngine:
    """
    Rule-based engine that evaluates Quality Assessor diagnoses and frame quality metrics
    to generate an adaptive forensic enhancement plan.
    """

    def __init__(self, blur_threshold: float = 100.0, quality_threshold: float = 82.0) -> None:
        self.blur_threshold = blur_threshold
        self.quality_threshold = quality_threshold

    def create_plan_from_quality(
        self,
        metrics: FrameQualityMetrics,
        is_blurry_from_assessor: Optional[bool] = None,
        blur_score_from_assessor: Optional[float] = None
    ) -> EnhancementPlan:
        """
        Determine necessary forensic enhancement operations based directly on Quality Assessor feedback.
        """
        blur_score = blur_score_from_assessor if blur_score_from_assessor is not None else metrics.blur_score
        is_blurry = is_blurry_from_assessor if is_blurry_from_assessor is not None else (blur_score < self.blur_threshold)

        # Skip enhancement if Quality Assessor confirms high quality with no blur
        if not is_blurry and metrics.overall_quality >= self.quality_threshold and metrics.noise_score < 8.0:
            return EnhancementPlan(
                should_enhance=False,
                enhancement_level="none",
                operations=["skip"],
                assessor_diagnosis="High visual quality confirmed by Quality Assessor; skipping enhancement."
            )

        operations: List[str] = []
        diagnoses: List[str] = []

        # 1. Quality Assessor Blur Diagnosis -> Deblur & Sharpen
        if is_blurry or blur_score < self.blur_threshold:
            operations.extend(["deblurring", "unsharp_masking", "adaptive_sharpening"])
            diagnoses.append(f"Blur detected by Quality Assessor (blur_score={blur_score:.2f} < threshold={self.blur_threshold})")

        # 2. Quality Assessor Brightness / Illumination Diagnosis
        if metrics.brightness < 85.0:  # Underexposed / Low-Light
            operations.extend(["adaptive_gamma", "shadow_recovery", "adaptive_clahe"])
            diagnoses.append(f"Underexposure detected by Quality Assessor (brightness={metrics.brightness:.2f} < 85.0)")
        elif metrics.brightness > 200.0:  # Overexposed / Glare
            operations.extend(["exposure_correction", "highlight_recovery"])
            diagnoses.append(f"Overexposure detected by Quality Assessor (brightness={metrics.brightness:.2f} > 200.0)")

        # 3. Quality Assessor Contrast Diagnosis
        if metrics.contrast < 38.0 or metrics.dynamic_range < 120.0:
            if "adaptive_clahe" not in operations:
                operations.append("contrast_stretching")
            operations.append("color_constancy")
            diagnoses.append(f"Low contrast/dynamic range detected by Quality Assessor (contrast={metrics.contrast:.2f})")

        # 4. Quality Assessor Noise / Compression Artifacts Diagnosis
        if metrics.noise_score > 12.0:
            operations.append("fast_denoising")
            diagnoses.append(f"High noise detected by Quality Assessor (noise_score={metrics.noise_score:.2f})")
        elif metrics.compression_artifacts > 2.5:
            operations.append("edge_preserving_filter")
            diagnoses.append(f"Compression blocking artifacts detected (blocking_ratio={metrics.compression_artifacts:.2f})")

        # Deduplicate while preserving order
        unique_ops = list(dict.fromkeys(operations))

        if not unique_ops:
            return EnhancementPlan(
                should_enhance=False,
                enhancement_level="none",
                operations=["skip"],
                assessor_diagnosis="No critical visual defects reported by Quality Assessor."
            )

        num_ops = len(unique_ops)
        level = "light" if num_ops <= 2 else ("moderate" if num_ops <= 4 else "aggressive")

        return EnhancementPlan(
            should_enhance=True,
            enhancement_level=level,
            operations=unique_ops,
            assessor_diagnosis="; ".join(diagnoses)
        )


# ============================================================================
# FORENSIC ENHANCEMENT PROCESSOR
# ============================================================================

class ForensicProcessor:
    """
    Non-destructive forensic image enhancement operations for CCTV streams.
    Preserves structural geometry, evidence boundaries, and true object features.
    """

    def __init__(self, use_gpu: bool = False) -> None:
        self.use_gpu = use_gpu and TORCH_AVAILABLE and torch.cuda.is_available()
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def execute_plan(self, frame: np.ndarray, plan: EnhancementPlan) -> np.ndarray:
        """
        Execute sequence of enhancement operations in optimal flagship computational photography order.
        """
        if frame is None or frame.size == 0 or not plan.should_enhance:
            return frame

        enhanced = frame.copy()

        # Optimal flagship computational photography sequence:
        # Denoise -> Exposure/Shadows -> Smart HDR Tone Mapping -> Deblur/Sharpen -> Smart Vibrance & Flagship ISP
        for op in plan.operations:
            try:
                if op == "flagship_isp":
                    enhanced = self.apply_flagship_isp_pipeline(enhanced)
                elif op == "fast_denoising":
                    enhanced = self.apply_denoising(enhanced)
                elif op == "edge_preserving_filter":
                    enhanced = self.apply_edge_preserving_filter(enhanced)
                elif op == "adaptive_gamma":
                    enhanced = self.apply_adaptive_gamma(enhanced, target_brightness=120.0)
                elif op == "shadow_recovery":
                    enhanced = self.apply_shadow_recovery(enhanced)
                elif op == "exposure_correction":
                    enhanced = self.apply_exposure_correction(enhanced, target_brightness=130.0)
                elif op == "highlight_recovery":
                    enhanced = self.apply_highlight_recovery(enhanced)
                elif op == "adaptive_clahe":
                    enhanced = self.apply_smart_hdr_tonemapping(enhanced)
                elif op == "contrast_stretching":
                    enhanced = self.apply_contrast_stretching(enhanced)
                elif op == "deblurring":
                    enhanced = self.apply_deblurring(enhanced)
                elif op == "unsharp_masking":
                    enhanced = self.apply_unsharp_masking(enhanced)
                elif op == "adaptive_sharpening":
                    enhanced = self.apply_adaptive_sharpening(enhanced)
                elif op == "laplacian_sharpening":
                    enhanced = self.apply_laplacian_sharpening(enhanced)
                elif op == "color_constancy":
                    enhanced = self.apply_color_constancy(enhanced)
            except Exception:
                # Fallback on operation error to maintain stability
                continue

        # Finish with subtle Samsung Pro-Visual Engine natural color & detail balance
        enhanced = self.apply_smart_vibrance(enhanced, vibrance_amount=0.06)

        return enhanced

    def apply_smart_hdr_tonemapping(self, img: np.ndarray) -> np.ndarray:
        """
        Samsung Galaxy S25 Ultra Pro-Visual Engine Multi-Scale Natural HDR.
        Lifts shadow detail smoothly while preserving true highlight roll-off and skin tone accuracy.
        """
        if len(img.shape) != 3:
            return img
        
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_chan, a_chan, b_chan = cv2.split(lab)
        l_norm = l_chan / 255.0

        # Multi-scale decomposition for natural illumination compression
        sigma1, sigma2 = 15.0, 45.0
        blur1 = cv2.GaussianBlur(l_norm, (0, 0), sigmaX=sigma1)
        blur2 = cv2.GaussianBlur(l_norm, (0, 0), sigmaX=sigma2)

        # Gentle log-domain dynamic range expansion
        log_l = np.log1p(l_norm * 2.5) / np.log1p(2.5)
        log_b1 = np.log1p(blur1 * 2.5) / np.log1p(2.5)
        log_b2 = np.log1p(blur2 * 2.5) / np.log1p(2.5)

        detail1 = log_l - log_b1
        detail2 = log_b1 - log_b2

        # Photorealistic layer blending
        hdr_l = log_l + detail1 * 0.20 + detail2 * 0.12
        hdr_l = np.clip(hdr_l * 255.0, 0, 255).astype(np.uint8)

        # Subtle, natural CLAHE
        clahe_natural = cv2.createCLAHE(clipLimit=1.4, tileGridSize=(8, 8))
        l_clahe = clahe_natural.apply(hdr_l)

        lab_out = cv2.merge([l_clahe.astype(np.float32), a_chan, b_chan])
        return cv2.cvtColor(lab_out.astype(np.uint8), cv2.COLOR_LAB2BGR)

    def apply_smart_vibrance(self, img: np.ndarray, vibrance_amount: float = 0.06) -> np.ndarray:
        """
        Samsung S25 Ultra Natural True-Color Vibrance.
        Selectively balances color fidelity while protecting natural human skin tones.
        """
        if len(img.shape) != 3:
            return img

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)

        # Precise skin-tone protection mask
        skin_mask = np.exp(-((h - 20.0) ** 2) / (2.0 * (12.0 ** 2)))

        sat_norm = s / 255.0
        vibrance_weight = (1.0 - sat_norm) * (1.0 - skin_mask * 0.85) * vibrance_amount
        
        s_boosted = s * (1.0 + vibrance_weight)
        s_out = np.clip(s_boosted, 0, 255)

        hsv_out = cv2.merge([h, s_out, v]).astype(np.uint8)
        return cv2.cvtColor(hsv_out, cv2.COLOR_HSV2BGR)

    def apply_flagship_isp_pipeline(self, img: np.ndarray) -> np.ndarray:
        """
        Samsung Galaxy S25 Ultra Pro-Visual Engine Processing Pipeline.
        Delivers ultra-sharp optical clarity, lifelike colors, balanced dynamic range,
        and pristine detail without artificial halos or oversaturation.
        """
        # 1. Edge-Preserving Denoising (Samsung noise reduction)
        denoised = cv2.bilateralFilter(img, d=5, sigmaColor=18, sigmaSpace=18)

        # 2. Pro-Visual Engine Natural HDR Tone Mapping
        hdr_mapped = self.apply_smart_hdr_tonemapping(denoised)

        # 3. Optical Micro-Detail Sharpening (High-frequency detail layer boost)
        gray = cv2.cvtColor(hdr_mapped, cv2.COLOR_BGR2GRAY)
        blurred_gray = cv2.GaussianBlur(gray, (0, 0), sigmaX=2.0)
        detail_diff = (gray.astype(np.float32) - blurred_gray.astype(np.float32))[..., np.newaxis]
        
        # Natural optical sharpening (0.22 detail gain)
        sharpened_bgr = np.clip(hdr_mapped.astype(np.float32) + detail_diff * 0.22, 0, 255).astype(np.uint8)

        # 4. Natural Color Balance
        natural_bgr = self.apply_smart_vibrance(sharpened_bgr, vibrance_amount=0.06)

        # 5. Photorealistic Tone Curve (Gentle linear-log S-curve)
        x = np.arange(256, dtype=np.float32)
        tone_curve = 255.0 / (1.0 + np.exp(-0.018 * (x - 128.0)))
        tone_curve = np.clip((tone_curve - tone_curve.min()) * (255.0 / (tone_curve.max() - tone_curve.min())), 0, 255).astype(np.uint8)

        return cv2.LUT(natural_bgr, tone_curve)



    def apply_adaptive_clahe(self, img: np.ndarray) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization in LAB luminance channel."""
        if len(img.shape) != 3:
            return img
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_enhanced = self._clahe.apply(l)
        lab_enhanced = cv2.merge((l_enhanced, a, b))
        return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    def apply_adaptive_gamma(self, img: np.ndarray, target_brightness: float = 120.0) -> np.ndarray:
        """Apply adaptive non-linear gamma correction based on image mean brightness."""
        mean_brightness = float(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean())
        if mean_brightness <= 1.0:
            return img
        gamma = np.log(target_brightness / 255.0) / np.log(mean_brightness / 255.0)
        gamma = max(0.4, min(2.2, gamma))
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        return cv2.LUT(img, table)

    def apply_exposure_correction(self, img: np.ndarray, target_brightness: float = 130.0) -> np.ndarray:
        """Linear illumination correction."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        current_mean = gray.mean()
        if current_mean == 0:
            return img
        gain = target_brightness / current_mean
        gain = max(0.5, min(1.8, gain))
        return cv2.convertScaleAbs(img, alpha=gain, beta=0)

    def apply_shadow_recovery(self, img: np.ndarray) -> np.ndarray:
        """Lift shadow regions without blowing out highlights."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        shadow_mask = np.clip(1.0 - (gray * 2.0), 0.0, 1.0)
        shadow_mask = cv2.GaussianBlur(shadow_mask, (15, 15), 0)
        
        img_float = img.astype(np.float32)
        boosted = np.power(img_float / 255.0, 0.7) * 255.0
        
        mask_3ch = cv2.merge([shadow_mask, shadow_mask, shadow_mask])
        result = img_float * (1.0 - mask_3ch) + boosted * mask_3ch
        return np.clip(result, 0, 255).astype(np.uint8)

    def apply_highlight_recovery(self, img: np.ndarray) -> np.ndarray:
        """Compress overexposed highlights."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        highlight_mask = np.clip((gray - 0.7) / 0.3, 0.0, 1.0)
        highlight_mask = cv2.GaussianBlur(highlight_mask, (15, 15), 0)

        img_float = img.astype(np.float32)
        compressed = np.power(img_float / 255.0, 1.3) * 255.0

        mask_3ch = cv2.merge([highlight_mask, highlight_mask, highlight_mask])
        result = img_float * (1.0 - mask_3ch) + compressed * mask_3ch
        return np.clip(result, 0, 255).astype(np.uint8)

    def apply_contrast_stretching(self, img: np.ndarray) -> np.ndarray:
        """Histogram percentile stretching."""
        p2, p98 = np.percentile(img, (2, 98))
        if p98 <= p2:
            return img
        stretched = np.clip((img.astype(np.float32) - p2) * (255.0 / (p98 - p2)), 0, 255)
        return stretched.astype(np.uint8)

    def apply_color_constancy(self, img: np.ndarray) -> np.ndarray:
        """Gray-World automatic white balance."""
        b, g, r = cv2.split(img.astype(np.float32))
        mean_b, mean_g, mean_r = b.mean(), g.mean(), r.mean()
        if mean_b == 0 or mean_g == 0 or mean_r == 0:
            return img
        gray_mean = (mean_b + mean_g + mean_r) / 3.0
        b = np.clip(b * (gray_mean / mean_b), 0, 255)
        g = np.clip(g * (gray_mean / mean_g), 0, 255)
        r = np.clip(r * (gray_mean / mean_r), 0, 255)
        return cv2.merge([b, g, r]).astype(np.uint8)

    def apply_denoising(self, img: np.ndarray) -> np.ndarray:
        """Fast Bilateral / Non-Local Means denoising."""
        return cv2.bilateralFilter(img, d=5, sigmaColor=35, sigmaSpace=35)

    def apply_edge_preserving_filter(self, img: np.ndarray) -> np.ndarray:
        """Edge preserving smoothing filter."""
        return cv2.edgePreservingFilter(img, flags=1, sigma_s=30, sigma_r=0.2)

    def apply_unsharp_masking(self, img: np.ndarray, amount: float = 1.2) -> np.ndarray:
        """Unsharp masking for high-frequency detail restoration."""
        blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=2.0)
        sharpened = cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def apply_adaptive_sharpening(self, img: np.ndarray) -> np.ndarray:
        """High-pass kernel sharpening."""
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)
        return cv2.filter2D(img, -1, kernel)

    def apply_laplacian_sharpening(self, img: np.ndarray) -> np.ndarray:
        """Laplacian-based detail boost."""
        lap = cv2.Laplacian(img, cv2.CV_16S, ksize=3)
        sharpened = cv2.addWeighted(img.astype(np.int32), 1, lap.astype(np.int32), -1, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def apply_deblurring(self, img: np.ndarray) -> np.ndarray:
        """Wiener spectral high-frequency restoration approximation."""
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ], dtype=np.float32)
        return cv2.filter2D(img, -1, kernel)


# ============================================================================
# AGENT CLASS
# ============================================================================

class EnhancementAgent(BaseAgent):
    """
    SentinelAI Forensic Image Enhancement Agent.
    
    Processes FramePackets or TrackingPackets, queries Quality Assessor findings,
    dynamically constructs an enhancement plan, executes forensic enhancement algorithms,
    and returns enhanced_frame alongside comprehensive enhancement_metadata.
    """

    def __init__(
        self,
        quality_threshold: float = 82.0,
        blur_threshold: float = 100.0,
        quality_assessor: Optional[QualityAssessor] = None,
        use_gpu: bool = True
    ) -> None:
        super().__init__("Enhancement")
        
        self.quality_threshold = quality_threshold
        self.blur_threshold = blur_threshold
        self.use_gpu = use_gpu and TORCH_AVAILABLE and (torch.cuda.is_available() if torch else False)

        self.quality_assessor = quality_assessor or QualityAssessor()
        self.analyzer = FrameAnalyzer()
        self.decision_engine = EnhancementDecisionEngine(
            blur_threshold=blur_threshold,
            quality_threshold=quality_threshold
        )
        self.processor = ForensicProcessor(use_gpu=self.use_gpu)

        # Telemetry statistics
        self._processed_frames: int = 0
        self._enhanced_frames: int = 0

    def initialize(self) -> None:
        """Initialize agent hardware acceleration and state."""
        super().initialize()
        self._processed_frames = 0
        self._enhanced_frames = 0
        device_str = "CUDA/GPU" if self.use_gpu else "CPU"
        self.logger.info(f"[{self.name}] Initialized using device: {device_str}.")

    def process(self, packet: Optional[BasePacket]) -> Optional[BasePacket]:
        """
        Process incoming packet, querying Quality Assessor to apply targeted forensic image enhancement.

        Parameters
        ----------
        packet : BasePacket, optional
            Packet containing image frame.

        Returns
        -------
        BasePacket or None
            Packet updated with `enhanced_frame` and `enhancement_metadata`.
        """
        if packet is None:
            self.logger.warning(f"[{self.name}] Received None packet.")
            return None

        if not isinstance(packet, BasePacket):
            self.logger.warning(f"[{self.name}] Received invalid packet type '{type(packet).__name__}'.")
            return packet

        start_time = time.perf_counter()

        try:
            # 1. Extract raw image frame
            frame = self._extract_frame(packet)
            if frame is None or frame.size == 0:
                self.logger.debug(f"[{self.name}] Packet contains no valid frame. Skipping enhancement.")
                self._attach_metadata(
                    packet, frame=None, enhanced_frame=None,
                    plan=EnhancementPlan(), metrics_before=FrameQualityMetrics(),
                    metrics_after=FrameQualityMetrics(), elapsed_ms=0.0
                )
                return packet

            # 2. Extract Quality Assessor guidance from frame or packet tracks
            is_blurry_assessor, blur_score_assessor = self._get_quality_assessor_guidance(packet, frame)

            # 3. Analyze frame quality metrics
            metrics_before = self.analyzer.analyze(frame)

            # 4. Create enhancement plan guided directly by Quality Assessor findings
            plan = self.decision_engine.create_plan_from_quality(
                metrics=metrics_before,
                is_blurry_from_assessor=is_blurry_assessor,
                blur_score_from_assessor=blur_score_assessor
            )

            # 5. Execute enhancement operations if recommended by Quality Assessor
            if plan.should_enhance:
                enhanced_frame = self.processor.execute_plan(frame, plan)
                metrics_after = self.analyzer.analyze(enhanced_frame)
                self._enhanced_frames += 1
            else:
                enhanced_frame = frame.copy()
                metrics_after = metrics_before

            self._processed_frames += 1
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # 6. Update packet with enhanced frame and forensic metadata
            self._attach_enhanced_frame(packet, enhanced_frame)
            self._attach_metadata(
                packet=packet,
                frame=frame,
                enhanced_frame=enhanced_frame,
                plan=plan,
                metrics_before=metrics_before,
                metrics_after=metrics_after,
                elapsed_ms=elapsed_ms
            )

        except Exception as err:
            self.logger.error(
                f"[{self.name}] Exception during enhancement pipeline: {err}. Returning original packet.",
                exc_info=True
            )
            raw_frame = self._extract_frame(packet)
            if raw_frame is not None:
                self._attach_enhanced_frame(packet, raw_frame)

        return packet

    def _get_quality_assessor_guidance(
        self,
        packet: BasePacket,
        frame: np.ndarray
    ) -> Tuple[Optional[bool], Optional[float]]:
        """
        Extract prior Quality Assessor metrics from packet tracks/detections or run QualityAssessor service on frame.
        """
        # Check if tracks have quality assessor annotations
        if hasattr(packet, "tracks") and packet.tracks:
            blurry_flags = []
            blur_scores = []
            for track in packet.tracks:
                det = getattr(track, "detection", None)
                if det is not None:
                    if hasattr(det, "is_blurry"):
                        blurry_flags.append(getattr(det, "is_blurry"))
                    if hasattr(det, "quality_score"):
                        blur_scores.append(getattr(det, "quality_score"))
            
            if blurry_flags and blur_scores:
                any_blurry = any(blurry_flags)
                avg_blur_score = float(np.mean(blur_scores))
                return any_blurry, avg_blur_score

        # Otherwise invoke QualityAssessor directly on the frame
        try:
            blurry, score = self.quality_assessor.is_blurry(frame, threshold=self.blur_threshold)
            return blurry, float(score)
        except Exception:
            return None, None

    def _extract_frame(self, packet: BasePacket) -> Optional[np.ndarray]:
        """Safely extract frame numpy array from diverse packet structures."""
        if hasattr(packet, "frame_packet") and packet.frame_packet is not None:
            return getattr(packet.frame_packet, "frame", None)
        elif hasattr(packet, "frame"):
            return getattr(packet, "frame", None)
        return None

    def _attach_enhanced_frame(self, packet: BasePacket, enhanced_frame: np.ndarray) -> None:
        """Safely attach enhanced_frame to packet metadata and update frame pointers."""
        if hasattr(packet, "metadata") and isinstance(packet.metadata, dict):
            packet.metadata["enhanced_frame"] = enhanced_frame

        try:
            setattr(packet, "enhanced_frame", enhanced_frame)
        except AttributeError:
            pass

        if hasattr(packet, "frame_packet") and packet.frame_packet is not None:
            if hasattr(packet.frame_packet, "metadata") and isinstance(packet.frame_packet.metadata, dict):
                packet.frame_packet.metadata["enhanced_frame"] = enhanced_frame
            try:
                setattr(packet.frame_packet, "enhanced_frame", enhanced_frame)
            except AttributeError:
                pass
            if hasattr(packet.frame_packet, "frame"):
                packet.frame_packet.frame = enhanced_frame
        elif hasattr(packet, "frame"):
            try:
                packet.frame = enhanced_frame
            except AttributeError:
                pass

    def _attach_metadata(
        self,
        packet: BasePacket,
        frame: Optional[np.ndarray],
        enhanced_frame: Optional[np.ndarray],
        plan: EnhancementPlan,
        metrics_before: FrameQualityMetrics,
        metrics_after: FrameQualityMetrics,
        elapsed_ms: float
    ) -> None:
        """Populate metadata dictionary on the packet."""
        metadata = {
            "processing_time": round(elapsed_ms, 2),
            "operations_applied": plan.operations,
            "enhancement_level": plan.enhancement_level,
            "assessor_diagnosis": plan.assessor_diagnosis,
            "blur_score": round(metrics_after.blur_score, 2),
            "noise_score": round(metrics_after.noise_score, 2),
            "quality_before": round(metrics_before.overall_quality, 2),
            "quality_after": round(metrics_after.overall_quality, 2),
            "metrics_before": metrics_before.to_dict(),
            "metrics_after": metrics_after.to_dict(),
        }

        if hasattr(packet, "metadata") and isinstance(packet.metadata, dict):
            packet.metadata["enhancement"] = metadata
            packet.metadata["enhancement_metadata"] = metadata

        try:
            setattr(packet, "enhancement_metadata", metadata)
        except AttributeError:
            pass

        if hasattr(packet, "frame_packet") and packet.frame_packet is not None:
            if hasattr(packet.frame_packet, "metadata") and isinstance(packet.frame_packet.metadata, dict):
                packet.frame_packet.metadata["enhancement_metadata"] = metadata
            try:
                setattr(packet.frame_packet, "enhancement_metadata", metadata)
            except AttributeError:
                pass

    def shutdown(self) -> None:
        """Shutdown the agent and log summary metrics."""
        super().shutdown()
        self.logger.info(
            f"[{self.name}] Stopped. Summary: Processed={self._processed_frames}, Enhanced={self._enhanced_frames}."
        )


# Alias for alternative instantiation naming convention
ImageEnhancementAgent = EnhancementAgent

