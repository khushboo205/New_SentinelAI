import logging
import threading
from typing import Any, Dict, Optional
from pathlib import Path

from ultralytics import YOLO

logger = logging.getLogger("SentinelAI.ModelManager")


class ModelManager:
    """
    Thread-safe singleton model registry.
    Manages lazy loading and caching of vision, OCR, face, and re-id models
    with device-appropriate inference contexts (CPU vs CUDA).
    """

    _instance: Optional["ModelManager"] = None
    _init_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.models: Dict[str, Any] = {}
                cls._instance._lock = threading.RLock()
            return cls._instance

    def _is_cuda_available(self) -> bool:
        try:
            import torch
            return bool(torch.cuda.is_available())
        except Exception:
            return False

    def load_yolo(self, model_name: str = "yolo11n.pt") -> YOLO:
        """Load and cache YOLO detection/tracking model."""
        key = f"yolo_{Path(model_name).name}"
        with self._lock:
            if key not in self.models:
                logger.info(f"Loading YOLO model: {model_name}")
                self.models[key] = YOLO(model_name)
            return self.models[key]

    def load_face(self) -> Optional[Any]:
        """
        Load InsightFace FaceAnalysis.
        Uses ctx_id=0 if CUDA is available, else ctx_id=-1 for CPU execution.
        """
        with self._lock:
            if "face" not in self.models:
                try:
                    from insightface.app import FaceAnalysis
                    cuda = self._is_cuda_available()
                    ctx_id = 0 if cuda else -1
                    logger.info(f"Loading InsightFace on {'GPU (ctx_id=0)' if cuda else 'CPU (ctx_id=-1)'}")
                    app = FaceAnalysis()
                    app.prepare(ctx_id=ctx_id)
                    self.models["face"] = app
                except Exception as exc:
                    logger.warning(f"InsightFace initialization deferred or failed: {exc}")
                    self.models["face"] = None
            return self.models["face"]

    def load_ocr(self) -> Optional[Any]:
        """Load EasyOCR reader with appropriate GPU flag."""
        with self._lock:
            if "ocr" not in self.models:
                try:
                    import easyocr
                    cuda = self._is_cuda_available()
                    logger.info(f"Loading EasyOCR on {'GPU' if cuda else 'CPU'}")
                    self.models["ocr"] = easyocr.Reader(["en"], gpu=cuda)
                except Exception as exc:
                    logger.warning(f"EasyOCR initialization deferred or failed: {exc}")
                    self.models["ocr"] = None
            return self.models["ocr"]

    def load_reid(self) -> Optional[Any]:
        """Placeholder for Re-ID feature extractor."""
        with self._lock:
            if "reid" not in self.models:
                self.models["reid"] = None
            return self.models["reid"]

    def get(self, name: str) -> Optional[Any]:
        """Get model by cached key."""
        with self._lock:
            return self.models.get(name)