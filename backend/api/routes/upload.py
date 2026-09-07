import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from services.pipeline_service import PipelineService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

UPLOAD_DIR = Path("data/videos/input")
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov"}

service = PipelineService()


def _is_valid_video_header(header: bytes) -> bool:
    """Validate video file signature against common container magic bytes."""
    if len(header) < 12:
        return False
    # MP4 / MOV (ftyp atom)
    if header[4:8] in (b"ftyp", b"moov", b"mdat", b"wide"):
        return True
    # AVI (RIFF ... AVI )
    if header[:4] == b"RIFF" and header[8:12] == b"AVI ":
        return True
    # MKV / WebM (EBML)
    if header[:4] == b"\x1a\x45\xdf\xa3":
        return True
    return False


@router.post("/")
async def upload_video(file: UploadFile = File(...)):
    """
    Secure video ingestion endpoint.
    Performs filename sanitization, size checks, magic byte validation,
    and initiates pipeline processing with cryptographic provenance.
    """
    # 1. Sanitize filename & extension
    raw_name = Path(file.filename or "uploaded_video.mp4").name
    ext = Path(raw_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / raw_name

    # 2. Stream to disk with size cap and magic-byte inspection
    sha256 = hashlib.sha256()
    total_bytes = 0
    header = b""

    try:
        with open(target_path, "wb") as buffer:
            while chunk := await file.read(65536):
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    buffer.close()
                    if target_path.exists():
                        target_path.unlink()
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)} MB.",
                    )
                if len(header) < 32:
                    header += chunk[: 32 - len(header)]
                sha256.update(chunk)
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        if target_path.exists():
            target_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(exc)}")

    # 3. Magic-byte verification
    if not _is_valid_video_header(header):
        if target_path.exists():
            target_path.unlink()
        raise HTTPException(
            status_code=400,
            detail="File content does not match valid video container magic bytes.",
        )

    file_hash = sha256.hexdigest()

    # 4. Pipeline Execution
    try:
        result = service.process_video(str(target_path), max_frames=150)
        return {
            "success": True,
            "filename": raw_name,
            "sha256": file_hash,
            "size_bytes": total_bytes,
            "pipeline_result": result,
            "tracks": result.get("tracks", []),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline processing failed: {str(exc)}",
        )