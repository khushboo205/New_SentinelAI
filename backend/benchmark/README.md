# SentinelAI Research & Benchmarking Suite

## 1. Overview
This benchmarking suite provides a reproducible, scientifically defensible evaluation harness for SentinelAI (Intelligent Border Video Analytics Platform — IBVAP). It quantifies the objective impact of adaptive CCTV image enhancement on:
1. Physical image quality metrics (full-reference on controlled targets and no-reference on field footage).
2. Downstream computer vision analytics (YOLO11 object detection and EasyOCR optical character recognition).
3. Computational performance and latency profiles (steady-state vs cold-start isolation).

---

## 2. Scientific Principles & Methodology

### 2.1 Full-Reference vs. No-Reference Quality Metrics
- **Controlled Synthetic Benchmark (Full-Reference):** Signal restoration is evaluated against a known authentic clean ground-truth reference subject to calibrated degradations.
  - **Peak Signal-to-Noise Ratio (PSNR):** Logarithmic ratio measuring pixel fidelity ($10 \log_{10}(255^2 / \text{MSE})$); higher is better.
  - **Mean Squared Error (MSE):** Euclidean squared pixel deviation; **lower is better**.
  - **Structural Similarity Index (SSIM):** Compares luminance, contrast, and structural patterns; higher is better.
  - *Critical Caveat:* Increased PSNR does **not** guarantee universal restoration success. Unsharp filtering and histogram expansion can increase PSNR and reduce MSE while simultaneously reducing SSIM due to edge overshoot and gradient distortion.
- **Field CCTV Evaluation (No-Reference):** In operational field footage, authentic clean ground truth does not exist. Measuring PSNR or SSIM against degraded originals measures mathematical divergence, not restoration. We measure physical, objective no-reference metrics:
  - **Laplacian Variance ($\sigma^2(\nabla^2 I)$):** High-frequency spatial gradient indicator. It quantifies edge energy rise and **must not** be interpreted as a direct percentage reduction in optical blur.
  - **Tenengrad Sharpness:** Mean Sobel gradient magnitude $\text{mean}(\sqrt{G_x^2 + G_y^2})$.
  - **RMS Contrast:** Standard deviation of luminance intensities.
  - **Luminance (Mean):** Average grayscale intensity across the frame.
  - **Noise Floor Std Dev (`noise_std`):** Standard deviation of residual fluctuations after $3 \times 3$ median filtering. Enhancement non-linearities often amplify noise residuals.
  - **No Fake Composite Scores:** No synthetic or arbitrary "quality improvement" score is generated.

### 2.2 Downstream Analytics Methodology
- **YOLO11 Object Detection:**
  - Real-world field CCTV frames lack ground-truth object annotations. Consequently, detection count differences and confidence shifts represent **condition-dependent downstream model responses** to altered contrast and edge gradients, **not** validated detection accuracy, precision, or recall.
  - Matched detections between original and enhanced frames require identical class labels and an **$\text{IoU} \ge 0.45$** overlap.
- **EasyOCR / ANPR Recognition:**
  - Evaluated on a controlled license plate target with verified ground truth (`DL-01-CV-2026`).
  - **OCR Confidence vs. Character Accuracy:** OCR confidence is the model's internal softmax token probability. Character accuracy is computed via normalized Levenshtein edit distance:
    $$\text{Accuracy} = \max\left(0.0, 1.0 - \frac{\text{Levenshtein}(T_{\text{pred}}, T_{\text{GT}})}{\operatorname{len}(T_{\text{GT}})}\right)$$
  - Shifts in model confidence without changes in character accuracy are documented as confidence shifts, not accuracy gains.

### 2.3 Latency & Performance Methodology
- **YOLO Warm-Up & Cold-Start Isolation:**
  - Before timing measurements, an explicit warm-up inference (`yolo_model.predict(source=dummy_640x640, ...)`) is executed.
  - This isolates one-time PyTorch weight loading, memory allocation, and JIT graph compilation into an explicitly reported **cold-start latency**.
  - All subsequent per-sample inferences represent **steady-state inference latency**, which is reported as the primary latency metric.
- **Enhancement Latency:**
  - The `Enhancer` engine is instantiated once prior to the benchmark loop.
  - Timers (`time.perf_counter()`) strictly wrap the image transformation execution (`enhancer.enhance(...)`).
  - Mean latency across all evaluated field samples is reported without fabricating unmeasured repeat-run statistics.

---

## 3. Experimental Parameters & Reproducibility Specification

| Parameter | Specification |
|---|---|
| **Deterministic Random Seed** | `np.random.seed(42)` |
| **Controlled Clean Reference** | $420 \times 140$ px synthetic license plate (`DL-01-CV-2026`) |
| **Synthetic Degradation Model** | Severe underexposure ($0.30\times$), Gaussian blur ($5\times 5$, $\sigma = 1.8$), Additive Gaussian noise ($\mathcal{N}(0, 12^2)$) |
| **Enhancement Profile** | `moderate` (CLAHE, unsharp/sharpening approximation, fast bilateral denoise) |
| **Deblurring Step Nature** | High-frequency / $3\times 3$ Laplacian sharpening approximation (`[-1,-1,-1; -1,9,-1; -1,-1,-1]`); **not** true Wiener spectral deconvolution |
| **YOLO Model Weights** | `yolo11n.pt` (COCO-pretrained, 80 classes) |
| **YOLO Confidence Threshold** | $0.25$ |
| **YOLO IoU Match Threshold** | $\text{IoU} \ge 0.45$ |
| **OCR Model Engine** | EasyOCR (CRAFT text detector + PyTorch ResNet recognizer, English/Latin) |
| **Hardware Environment** | Local Host CPU Execution (AMD64, 16 logical cores) |
| **Software Stack** | Python 3.12.7, PyTorch 2.13.0+cpu, OpenCV 5.0.0 (`opencv-python-headless`), Ultralytics 8.3+, EasyOCR 1.7+, Scikit-Image 0.24+ |

### Dataset / Evaluated Field Samples
1. `sample_cctv_lowlight.jpg` ($478 \times 850$) — Severe low-light surveillance feed
2. `sample_cctv_blur.jpg` ($478 \times 850$) — Optical motion blur condition
3. `sample_cctv_fog.jpg` ($478 \times 850$) — Low-contrast atmospheric scattering
4. `sample_cctv_raw.jpg` ($478 \times 850$) — Baseline raw sensor surveillance capture
5. `market.jpg` ($1280 \times 853$) — High-density pedestrian and vehicle scene
6. `img2.jpeg` ($577 \times 1280$) — Wide perimeter security view

---

## 4. Execution & Verification

To execute the scientific benchmark suite from the backend directory:
```powershell
python benchmark/runner.py --run-all
```

To execute with alternate enhancement profiles:
```powershell
python benchmark/runner.py --run-all --level light
python benchmark/runner.py --run-all --level aggressive
```

### Artifact Outputs
- `backend/benchmark/results/enhancement_metrics.json`: Quantitative no-reference and full-reference readings.
- `backend/benchmark/results/detection_comparison.json`: Object-level detections, confidences, and IoU-matched pairs.
- `backend/benchmark/results/ocr_comparison.json`: Text extraction comparisons, Levenshtein edit distances, and character accuracies.
- `backend/benchmark/results/performance_metrics.json`: Steady-state vs cold-start latency breakdowns and throughput.
- `backend/benchmark/results/benchmark_summary.json`: Unified structured summary payload.
- `backend/benchmark/results/research_tables.md`: Publication-ready formatted research tables (Tables I, II, III, and IV).
- `backend/benchmark/derivatives/`: Cryptographically verified enhanced frames with SHA-256 hashes.

---

## 5. Methodological Limitations & Scientific Integrity
1. **Absence of Field Ground Truth:** Field CCTV footage lacks ground-truth bounding box annotations. Bounding box count and confidence shifts indicate downstream model sensitivity to image transforms, not guaranteed detection improvements.
2. **Sharpness vs. Noise:** Laplacian variance and Tenengrad metrics elevate when noise increases. They are gradient energy indicators, not optical blur removal percentages.
3. **SSIM Trade-off:** High-frequency edge sharpening can reduce SSIM while increasing PSNR.
4. **Algorithmic Scope:** The enhancement pipeline utilizes spatial unsharp masking approximations; it does not implement true iterative or spectral Wiener deconvolution.
