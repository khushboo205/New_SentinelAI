"""
SentinelAI Packet System

Every agent communicates using packet objects.

Author: SentinelAI
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.models import (
    Detection,
    Track,
    ReIDResult,
    Feature,
)


# ==========================================================
# Base Packet
# ==========================================================

@dataclass(slots=True)
class BasePacket:
    """
    Base class inherited by every packet.
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)

    source_agent: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Frame Packet
# ==========================================================

@dataclass(slots=True)
class FramePacket(BasePacket):
    """
    Raw frame coming from InputManager.
    """

    frame_id: int = 0

    frame: Optional[Any] = None

    width: int = 0

    height: int = 0

    fps: float = 0.0

    camera_id: str = ""

    video_name: str = ""

    @property
    def frame_number(self) -> int:
        return self.frame_id

    @frame_number.setter
    def frame_number(self, value: int) -> None:
        self.frame_id = value


# ==========================================================
# Detection Packet
# ==========================================================

@dataclass(slots=True)
class DetectionPacket(BasePacket):
    """
    Frame + detections
    """

    frame_packet: Optional[FramePacket] = None

    detections: List[Detection] = field(default_factory=list)


# ==========================================================
# Tracking Packet
# ==========================================================

@dataclass(slots=True)
class TrackingPacket(BasePacket):
    """
    Frame + tracks
    """

    frame_packet: Optional[FramePacket] = None

    tracks: List[Track] = field(default_factory=list)


# ==========================================================
# ReID Packet
# ==========================================================

@dataclass(slots=True)
class ReIDPacket(BasePacket):
    """
    Tracking results + identity embeddings
    """

    frame_packet: Optional[FramePacket] = None

    reid_results: List[ReIDResult] = field(default_factory=list)


# ==========================================================
# Feature Packet
# ==========================================================

@dataclass(slots=True)
class FeaturePacket(BasePacket):
    """
    High-level semantic features.
    """

    frame_packet: Optional[FramePacket] = None

    features: List[Feature] = field(default_factory=list)