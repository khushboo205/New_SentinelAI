"""
Enhancement API Routes

POST /enhancement/analyze  — analyze image quality, return metrics + diagnosis
POST /enhancement/run      — run enhancement pipeline, return enhanced image
GET  /enhancement/status   — return engine readiness
"""

from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from services.enhancement_api import EnhancementAPIService

router = APIRouter(
    prefix="/enhancement",
    tags=["Enhancement"],
)

_service = EnhancementAPIService()

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}


def _validate_image(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Upload JPEG or PNG.",
        )


import os
from fastapi.responses import FileResponse, Response

TEST_SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "test_samples")


@router.get("/status")
async def enhancement_status():
    """Return the readiness status of the enhancement engine."""
    return _service.status()


@router.get("/sample-image/{sample_id}")
async def get_sample_image(sample_id: str):
    """Return a real degraded CCTV test frame."""
    mapping = {
        "lowlight": "sample_cctv_lowlight.jpg",
        "blur": "sample_cctv_blur.jpg",
        "fog": "sample_cctv_fog.jpg",
        "raw": "sample_cctv_raw.jpg",
    }
    filename = mapping.get(sample_id.lower(), "sample_cctv_lowlight.jpg")
    filepath = os.path.join(TEST_SAMPLES_DIR, filename)
    if not os.path.exists(filepath):
        # Fallback to market.jpg
        filepath = os.path.join(os.path.dirname(TEST_SAMPLES_DIR), "images", "market.jpg")
    return FileResponse(filepath, media_type="image/jpeg")


_enhanced_cache: dict[str, bytes] = {}


@router.get("/sample-image-enhanced/{sample_id}")
async def get_sample_image_enhanced(sample_id: str):
    """Return an authentic enhanced derivative frame for the sample."""
    sid = sample_id.lower()
    if sid in _enhanced_cache:
        return Response(content=_enhanced_cache[sid], media_type="image/jpeg")

    mapping = {
        "lowlight": "sample_cctv_lowlight.jpg",
        "blur": "sample_cctv_blur.jpg",
        "fog": "sample_cctv_fog.jpg",
        "raw": "sample_cctv_raw.jpg",
    }
    filename = mapping.get(sid, "sample_cctv_lowlight.jpg")
    filepath = os.path.join(TEST_SAMPLES_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(os.path.dirname(TEST_SAMPLES_DIR), "images", "market.jpg")

    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        res = _service.run(raw_bytes)
        b64_str = res.get("enhanced", {}).get("image_base64", "")
        if b64_str:
            import base64
            enh_bytes = base64.b64decode(b64_str)
            _enhanced_cache[sid] = enh_bytes
            return Response(content=enh_bytes, media_type="image/jpeg")
    except Exception:
        pass
    return FileResponse(filepath, media_type="image/jpeg")


@router.post("/analyze")
async def analyze_quality(file: UploadFile = File(...)):
    """
    Analyze the quality of an uploaded image.

    Returns:
    - resolution
    - per-metric quality scores (blur, noise, brightness, contrast, etc.)
    - overall quality score (0-100)
    - quality label (POOR / DEGRADED / ACCEPTABLE / GOOD)
    - diagnosis chips with severity
    - recommended enhancement pipeline
    """
    _validate_image(file)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    result = _service.analyze(image_bytes)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result


@router.post("/run")
@router.post("/enhance")
async def run_enhancement(
    file: UploadFile = File(...),
    enhancement_level: Optional[str] = None,
):
    """
    Run the adaptive enhancement pipeline on an uploaded image.

    Returns:
    - source image (base64) with quality metrics and integrity hash
    - enhanced image (base64) with quality metrics and integrity hash
    - processing metadata (operations applied, time, engine)
    - validation proof (before/after hashes, on-disk file persistence)
    """
    _validate_image(file)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    result = _service.run(image_bytes, enhancement_level=enhancement_level)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result


@router.get("/derivative/{image_hash}")
async def get_derivative_image(image_hash: str):
    """Fetch an on-disk enhanced forensic derivative image by SHA-256 hash."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    clean_hash = "".join(c for c in image_hash if c.isalnum())
    filepath = os.path.join(base_dir, "data", "enhanced", f"{clean_hash}.jpg")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Derivative image not found on disk.")
    return FileResponse(filepath, media_type="image/jpeg")
