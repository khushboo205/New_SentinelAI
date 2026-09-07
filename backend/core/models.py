from __future__ import annotations

from dataclasses import dataclass,field
from typing import List, Optional, Any

# ==========================================================
# Detection
# ==========================================================
@dataclass(slots=True)
class Detection:
    """
    Single object detected by YOLO.
    """

    # Detection
    bbox: tuple[float, float, float, float]
    confidence: float
    class_id: int
    class_name: str
    track_id: Optional[int] = None
    behavior: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    quality: dict = field(default_factory=dict)

    # Image
    crop: Optional[Any] = None

    # Quality
    quality_score: float = 0.0
    is_blurry: bool = False

    # OCR
    ocr_text: list[str] = field(default_factory=list)
    ocr_confidence: float = 0.0

    # Face
    face_detected: bool = False
    face_identity: Optional[str] = None
    face_confidence: float = 0.0
    face_embedding: Optional[Any] = None

    reid_embedding: object | None = None

    # Attributes
    attributes: dict = field(default_factory=dict)

    # Events
    events: list[Any] = field(default_factory=list)

    # Risk & Suspicion
    risk_score: float = 0.0
    risk_level: str = "Low"
    alert: bool = False
    is_suspicious: bool = False
    reasons: list[str] = field(default_factory=list)
    risk_reasons: list[str] = field(default_factory=list)
    contributing_factors: list[dict] = field(default_factory=list)

    # Contextual & Movement
    zone: str = ""
    is_loitering: bool = False
    speed_kmh: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation for API serialization."""
        return {
            "bbox": list(self.bbox) if self.bbox else [],
            "confidence": round(float(self.confidence), 4),
            "class_id": int(self.class_id),
            "class_name": self.class_name,
            "track_id": self.track_id,
            "quality_score": round(float(self.quality_score), 2),
            "is_blurry": self.is_blurry,
            "ocr_text": self.ocr_text,
            "ocr_confidence": round(float(self.ocr_confidence), 4),
            "face_detected": self.face_detected,
            "face_identity": self.face_identity,
            "face_confidence": round(float(self.face_confidence), 4),
            "attributes": self.attributes,
            "events": self.events,
            "risk_score": round(float(self.risk_score), 2),
            "risk_level": self.risk_level,
            "alert": self.alert,
            "is_suspicious": self.is_suspicious,
            "reasons": self.reasons,
            "contributing_factors": self.contributing_factors,
            "zone": self.zone,
        }
# ==========================================================
# Track
# ==========================================================

@dataclass(slots=True)
class Track:
    """
    Represents one tracked object.
    """

    track_id: int

    detection: Detection

    first_seen: int = 0

    last_seen: int = 0

    age: int = 0

    active: bool = True


# ==========================================================
# ReID Result
# ==========================================================

@dataclass(slots=True)
class ReIDResult:
    """
    Identity information produced by the ReID agent.
    """
    track_id: int

    embedding: Optional[Any] = None

    identity: Optional[str] = None

    similarity: float = 0.0


# ==========================================================
# Feature
# ==========================================================

@dataclass(slots=True)
class Feature:
    """
    Semantic information extracted from an object.
    """

    track_id: int

    shirt_color: str = ""

    pant_color: str = ""

    bag: bool = False

    helmet: bool = False

    face_visible: bool = False

    clip_embedding: Optional[Any] = None