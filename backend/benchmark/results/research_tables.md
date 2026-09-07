# SentinelAI Scientific Benchmark Results
**Generated:** 2026-09-05 05:57:27 UTC
**Execution Hardware:** Intel64 Family 6 Model 154 Stepping 3, GenuineIntel (AMD64) | Python 3.12.7 | PyTorch 2.13.0+cpu (CUDA: False)

## Table I: Image Enhancement Quality Comparison
*Controlled full-reference metrics against authentic clean ground truth & objective physical no-reference metrics on field CCTV footage.*

| Dataset / Sample | Quality Metric | Original / Degraded | Enhanced Derivative | Metric Change | Impact Summary |
|---|---|:---:|:---:|:---:|---|
| **Controlled Plate** (Ref) | PSNR (Fidelity; higher is better) | 4.6 dB | 6.42 dB | **+1.82 dB** | Signal-to-Noise recovery |
| **Controlled Plate** (Ref) | SSIM (Structural; higher is better) | 0.2334 | 0.1509 | **-0.0825** | Structural fidelity reduction (edge overshoot) |
| **Controlled Plate** (Ref) | MSE (Pixel Error; lower is better) | 22540.935 | 14839.363 | **-7701.57** (reduced by 7701.57) | Error reduction (lower is better) |
| `sample_cctv_lowlight.jpg` | Laplacian Variance (Sharpness Indicator) | 2900.05 | 297738.1 | +294838.05 | High-frequency edge gradient rise |
| `sample_cctv_lowlight.jpg` | Tenengrad Sharpness (Gradient Energy) | 54.1 | 351.98 | +297.88 | Gradient magnitude mean |
| `sample_cctv_lowlight.jpg` | RMS Contrast (Dynamic Spread) | 24.15 | 104.31 | +80.16 (+331.9%) | Dynamic range expansion (+331.9%) |
| `sample_cctv_lowlight.jpg` | Luminance (Mean Intensity) | 46.44 | 111.28 | +64.84 | Illumination redistribution |
| `sample_cctv_lowlight.jpg` | Noise Floor Std Dev (Residual) | 11.68 | 113.21 | +101.53 (+869.3%) | High-frequency noise/residual increase |
| `sample_cctv_blur.jpg` | Laplacian Variance (Sharpness Indicator) | 72.3 | 1642.88 | +1570.58 | High-frequency edge gradient rise |
| `sample_cctv_blur.jpg` | Tenengrad Sharpness (Gradient Energy) | 18.01 | 46.92 | +28.91 | Gradient magnitude mean |
| `sample_cctv_blur.jpg` | RMS Contrast (Dynamic Spread) | 60.72 | 59.38 | -1.34 (-2.2%) | Local contrast slight contraction (-2.2%) |
| `sample_cctv_blur.jpg` | Luminance (Mean Intensity) | 133.93 | 160.89 | +26.96 | Illumination redistribution |
| `sample_cctv_blur.jpg` | Noise Floor Std Dev (Residual) | 2.12 | 10.87 | +8.75 (+412.7%) | High-frequency noise/residual increase |
| `sample_cctv_fog.jpg` | Laplacian Variance (Sharpness Indicator) | 188.68 | 6210.63 | +6021.95 | High-frequency edge gradient rise |
| `sample_cctv_fog.jpg` | Tenengrad Sharpness (Gradient Energy) | 14.56 | 45.14 | +30.58 | Gradient magnitude mean |
| `sample_cctv_fog.jpg` | RMS Contrast (Dynamic Spread) | 28.09 | 35.06 | +6.97 (+24.8%) | Dynamic range expansion (+24.8%) |
| `sample_cctv_fog.jpg` | Luminance (Mean Intensity) | 170.28 | 190.7 | +20.42 | Illumination redistribution |
| `sample_cctv_fog.jpg` | Noise Floor Std Dev (Residual) | 3.07 | 16.95 | +13.88 (+452.1%) | High-frequency noise/residual increase |
| `sample_cctv_raw.jpg` | Laplacian Variance (Sharpness Indicator) | 876.46 | 20019.29 | +19142.83 | High-frequency edge gradient rise |
| `sample_cctv_raw.jpg` | Tenengrad Sharpness (Gradient Energy) | 31.75 | 96.58 | +64.83 | Gradient magnitude mean |
| `sample_cctv_raw.jpg` | RMS Contrast (Dynamic Spread) | 62.36 | 64.19 | +1.83 (+2.9%) | Dynamic range expansion (+2.9%) |
| `sample_cctv_raw.jpg` | Luminance (Mean Intensity) | 133.92 | 162.98 | +29.06 | Illumination redistribution |
| `sample_cctv_raw.jpg` | Noise Floor Std Dev (Residual) | 6.62 | 31.67 | +25.05 (+378.4%) | High-frequency noise/residual increase |
| `market.jpg` | Laplacian Variance (Sharpness Indicator) | 1292.92 | 28307.3 | +27014.38 | High-frequency edge gradient rise |
| `market.jpg` | Tenengrad Sharpness (Gradient Energy) | 90.5 | 218.21 | +127.71 | Gradient magnitude mean |
| `market.jpg` | RMS Contrast (Dynamic Spread) | 58.03 | 80.33 | +22.30 (+38.4%) | Dynamic range expansion (+38.4%) |
| `market.jpg` | Luminance (Mean Intensity) | 116.14 | 132.5 | +16.36 | Illumination redistribution |
| `market.jpg` | Noise Floor Std Dev (Residual) | 8.48 | 38.29 | +29.81 (+351.5%) | High-frequency noise/residual increase |
| `img2.jpeg` | Laplacian Variance (Sharpness Indicator) | 76.22 | 2395.13 | +2318.91 | High-frequency edge gradient rise |
| `img2.jpeg` | Tenengrad Sharpness (Gradient Energy) | 40.94 | 90.42 | +49.48 | Gradient magnitude mean |
| `img2.jpeg` | RMS Contrast (Dynamic Spread) | 38.31 | 50.53 | +12.22 (+31.9%) | Dynamic range expansion (+31.9%) |
| `img2.jpeg` | Luminance (Mean Intensity) | 161.73 | 169.03 | +7.30 | Illumination redistribution |
| `img2.jpeg` | Noise Floor Std Dev (Residual) | 2.15 | 9.47 | +7.32 (+340.5%) | High-frequency noise/residual increase |

*Methodological Note: Laplacian variance and Tenengrad measure high-frequency spatial gradients and edge energy. They do not constitute linear percentage reductions in optical blur. Increased PSNR reflects pixel error reduction but does not imply universal restoration success, as SSIM decreased due to sharpening edge artifacts. Noise floor standard deviation indicates high-frequency residual amplification after non-linear filtering.*

---

## Table II: Downstream Object Detection Response (YOLO11)
*Evaluation of object detection counts and confidence shifts on identical image inputs. Real-world CCTV footage lacks ground-truth bounding box annotations; metrics reflect condition-dependent downstream model responses rather than verified detection accuracy or precision/recall.*

| Sample CCTV Feed | Original Detections | Enhanced Detections | Mean Conf (Orig) | Mean Conf (Enh) | Conf Delta | Matched Overlaps (IoU ≥ 0.45) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `sample_cctv_lowlight.jpg` | 1 | 0 | 0.4228 | 0.0000 | -0.4228 | 0 matched (-1 dropped) |
| `sample_cctv_blur.jpg` | 0 | 0 | 0.0000 | 0.0000 | +0.0000 | 0 matched |
| `sample_cctv_fog.jpg` | 0 | 0 | 0.0000 | 0.0000 | +0.0000 | 0 matched |
| `sample_cctv_raw.jpg` | 1 | 1 | 0.4248 | 0.3698 | -0.0550 | 1 matched |
| `market.jpg` | 7 | 5 | 0.5524 | 0.6152 | +0.0628 | 5 matched (-2 dropped) |
| `img2.jpeg` | 1 | 1 | 0.5797 | 0.3722 | -0.2075 | 0 matched (+1 new) (-1 dropped) |

*Scientific Finding: Real-world field CCTV frames lack ground-truth object annotations. Detection differences reflect condition-dependent model responses to altered contrast and edge gradients rather than validated precision or recall. Pre-trained COCO YOLO detectors are sensitive to unsharp edge artifacts; enhancement alters local features without guaranteeing confidence increases across all classes without domain fine-tuning. Matched detections require IoU ≥ 0.45 with matching class labels.*

---

## Table III: OCR / ANPR Downstream Text Extraction Comparison
*EasyOCR recognition comparison against verified ground-truth text on degraded vs enhanced crops. Distinguishes model confidence from character accuracy.*

| Test Subject | Ground Truth | Degraded Extraction | Enhanced Extraction | Degraded Conf | Enhanced Conf | Character Accuracy (Enh vs Deg) |
|---|---|---|---|:---:|:---:|:---:|
| **Synthetic Night Plate** | `DL-01-CV-2026` | `IN DL-01-CV-2026` | `OL01-Cvp026` | 0.6836 | 0.1267 | 80.0% vs 80.0% (Δ +0.0%) |

*Scientific Finding: While Levenshtein-based character accuracy remained unchanged at 80.0% (Δ 0.0%, edit distance = 2 against ground truth 'DL-01-CV-2026'), OCR model confidence declined from 0.6836 to 0.1267 (Δ -0.5569) due to high-frequency edge artifacts along character boundaries. Enhancement did not improve text extraction accuracy on this sample, highlighting the critical distinction between model confidence and objective character accuracy.*

---

## Table IV: Computational Performance & Latency Profile
*Component execution latency measured on local CPU execution environment. Steady-state measurements are isolated from cold-start model initialization via explicit warm-up.*

| Pipeline Component | Operation Mode | Mean Latency (ms) | Throughput (FPS) | Implementation Target |
|---|---|:---:|:---:|---|
| **SentinelAI Enhancer** | Moderate Profile (CLAHE + Sharp + Fast Denoise) | 228.06 ms | 4.4 FPS | CPU / OpenCV C++ Core |
| **YOLO11 Detector (Steady-State)** | Inference (yolo11n.pt, conf=0.25) | 53.05 ms | 18.8 FPS | CPU / PyTorch TorchScript |
| **YOLO11 Detector (Cold-Start)** | Model Load & Initial JIT Inference | 1921.08 ms | N/A (One-Time) | CPU / PyTorch Model Initialization |
| **EasyOCR Reader** | Latin / English Text Recognition | 303.81 ms | 3.3 FPS | CPU / CRAFT + PyTorch ResNet |
| **Composite Steady-State Pipeline** | Enhance + YOLO Detection Combined | 281.11 ms | 3.6 FPS | Full CCTV Analytic Pass |

---
