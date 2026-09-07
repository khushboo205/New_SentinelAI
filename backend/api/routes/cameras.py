"""
Cameras API Route

GET /cameras — return list of configured cameras with optical quality states
"""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"],
)

CAMERAS_DATA = [
    {
        "id": "CAM_01",
        "name": "Perimeter Fence - Sector North",
        "location": "Sector 04 — North Boundary",
        "status": "online",
        "stream_type": "optical_rtsp",
        "resolution": "1920x1080",
        "fps": 25,
        "quality_score": 38.2,
        "quality_label": "DEGRADED",
        "degradations": ["LOW LIGHT", "HIGH NOISE", "NARROW DYNAMIC RANGE"],
        "recommended_pipeline": ["Low-light gamma", "Bilateral Denoise", "HDR Tone Map", "Sharpening"],
        "active_targets": 2,
        "sample_id": "lowlight",
        "sample_url": "/enhancement/sample-image/lowlight",
        "last_activity": "21:31:04",
        "risk_level": "High"
    },
    {
        "id": "CAM_02",
        "name": "Checkpoint Alpha - Fast Lane",
        "location": "Gate 01 — Vehicle Ingress",
        "status": "online",
        "stream_type": "anpr_ir",
        "resolution": "1920x1080",
        "fps": 30,
        "quality_score": 45.0,
        "quality_label": "DEGRADED",
        "degradations": ["HIGH MOTION BLUR", "MODERATE COMPRESSION"],
        "recommended_pipeline": ["Kernel Sharpening (3x3)", "Edge Filter", "Adaptive Sharpening"],
        "active_targets": 1,
        "sample_id": "blur",
        "sample_url": "/enhancement/sample-image/blur",
        "last_activity": "21:31:17",
        "risk_level": "Critical"
    },
    {
        "id": "CAM_03",
        "name": "Buffer Zone - River Marsh",
        "location": "Sector 09 — Wetland Perimeter",
        "status": "online",
        "stream_type": "cctv_optical",
        "resolution": "1280x720",
        "fps": 20,
        "quality_score": 51.4,
        "quality_label": "DEGRADED",
        "degradations": ["ATMOSPHERIC HAZE / FOG", "LOW CONTRAST"],
        "recommended_pipeline": ["Contrast Stretching", "Dark Channel Dehaze", "Unsharp Masking"],
        "active_targets": 0,
        "sample_id": "fog",
        "sample_url": "/enhancement/sample-image/fog",
        "last_activity": "21:28:50",
        "risk_level": "Medium"
    },
    {
        "id": "CAM_04",
        "name": "Loading Yard & Cargo Dock",
        "location": "Logistics Depot — Bay 03",
        "status": "online",
        "stream_type": "optical_4k",
        "resolution": "2560x1440",
        "fps": 25,
        "quality_score": 84.1,
        "quality_label": "NOMINAL",
        "degradations": [],
        "recommended_pipeline": ["Pass-through (No enhancement required)"],
        "active_targets": 3,
        "sample_id": "raw",
        "sample_url": "/enhancement/sample-image/raw",
        "last_activity": "21:32:00",
        "risk_level": "Low"
    }
]

from database.repository import Repository

_repo = Repository()

@router.get("/")
async def get_cameras():
    """Return all surveillance cameras from database with diagnostic optical quality states."""
    cams = _repo.get_cameras()
    if not cams:
        cams = CAMERAS_DATA
    return {
        "count": len(cams),
        "cameras": cams
    }

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    """Get single camera details from database repository."""
    cam = _repo.get_camera(camera_id)
    if not cam:
        cam = next((c for c in CAMERAS_DATA if c["id"].upper() == camera_id.upper()), None)
    if not cam:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam
