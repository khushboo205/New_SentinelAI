"""
SentinelAI Transparent Rule-Based Risk Engine

Evaluates surveillance tracks against deterministic contributing factors:
- night_period: Activity during nighttime operational windows (20:00 - 06:00)
- restricted_zone: Movement inside exclusion or buffer zones
- loitering: Target stationary or meandering beyond dwell threshold
- degraded_footage: Evidence source severely compromised by blur/noise
- unverified_reid: Person present without verified biometric or badge record
- high_speed_movement: Abnormal rapid motion along perimeter boundary
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.agent import BaseAgent
from core.packet import TrackingPacket


class RuleBasedRiskEngine:
    """
    Transparent, auditable rule-based risk evaluation engine.
    Calculates composite threat scores with full attribution of contributing factors.
    """

    FACTOR_WEIGHTS = {
        "restricted_zone": 35,
        "night_period": 20,
        "loitering": 25,
        "high_speed_movement": 20,
        "unverified_reid": 15,
        "degraded_footage": 15,
    }

    def evaluate(
        self,
        night_period: bool = False,
        restricted_zone: bool = False,
        loitering: bool = False,
        degraded_footage: bool = False,
        unverified_reid: bool = False,
        high_speed_movement: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate risk with explicit contributing factor attribution.
        """
        meta = metadata or {}
        raw_score = 0
        factors: List[Dict[str, Any]] = []

        if restricted_zone:
            pts = self.FACTOR_WEIGHTS["restricted_zone"]
            raw_score += pts
            factors.append({
                "factor": "restricted_zone",
                "label": "Restricted Zone Intrusion",
                "weight": pts,
                "description": meta.get("zone_desc", "Track located inside restricted perimeter perimeter/buffer zone."),
            })

        if loitering:
            pts = self.FACTOR_WEIGHTS["loitering"]
            raw_score += pts
            factors.append({
                "factor": "loitering",
                "label": "Prolonged Loitering / Dwell Time",
                "weight": pts,
                "description": meta.get("loiter_desc", "Target stationary or pacing within sector exceeding dwell threshold."),
            })

        if night_period:
            pts = self.FACTOR_WEIGHTS["night_period"]
            raw_score += pts
            factors.append({
                "factor": "night_period",
                "label": "Night Period Operation",
                "weight": pts,
                "description": meta.get("time_desc", "Incident occurred during designated night surveillance window (20:00 - 06:00)."),
            })

        if high_speed_movement:
            pts = self.FACTOR_WEIGHTS["high_speed_movement"]
            raw_score += pts
            factors.append({
                "factor": "high_speed_movement",
                "label": "High-Speed / Evasive Movement",
                "weight": pts,
                "description": meta.get("speed_desc", "Abnormal rapid trajectory acceleration detected near perimeter boundary."),
            })

        if unverified_reid:
            pts = self.FACTOR_WEIGHTS["unverified_reid"]
            raw_score += pts
            factors.append({
                "factor": "unverified_reid",
                "label": "Unverified Re-ID / Unidentified Subject",
                "weight": pts,
                "description": meta.get("reid_desc", "Person detected with no matching registered biometric or credential signature."),
            })

        if degraded_footage:
            pts = self.FACTOR_WEIGHTS["degraded_footage"]
            raw_score += pts
            factors.append({
                "factor": "degraded_footage",
                "label": "Degraded Surveillance Footage",
                "weight": pts,
                "description": meta.get("footage_desc", "Sensor feed degraded by severe blur or sensor noise obscuring facial features."),
            })

        clamped_score = min(100, raw_score)

        if clamped_score >= 75:
            level = "Critical"
        elif clamped_score >= 50:
            level = "High"
        elif clamped_score >= 25:
            level = "Medium"
        else:
            level = "Low"

        return {
            "score": clamped_score,
            "raw_score": raw_score,
            "risk_level": level,
            "is_suspicious": clamped_score >= 50,
            "contributing_factors": factors,
            "factor_count": len(factors),
            "engine": "RuleBasedRiskEngine (deterministic)",
        }


class SuspicionAgent(BaseAgent):
    """
    Pipeline Agent executing the RuleBasedRiskEngine over tracked targets.
    """

    def __init__(self):
        super().__init__("SuspicionAgent")
        self.engine = RuleBasedRiskEngine()

    def process(self, packet: TrackingPacket):
        for track in packet.tracks:
            detection = track.detection

            # Extract or infer indicators
            is_night = False
            now = datetime.datetime.now().time()
            if now >= datetime.time(20, 0) or now <= datetime.time(6, 0):
                is_night = True

            zone = getattr(detection, "zone", "") or ""
            is_restricted = any(kw in zone.lower() for kw in ["restricted", "perimeter", "ravine", "fence", "sector a", "buffer"])

            # Loitering based on track duration or stationary flag
            duration = getattr(track, "duration_sec", 0) or 0
            is_loitering = duration > 30.0 or getattr(detection, "is_loitering", False)

            # Degraded footage
            is_degraded = getattr(detection, "is_blurry", False) or (getattr(detection, "quality_score", 100) < 40)

            # Re-ID status
            face_det = getattr(detection, "face_detected", False)
            identity = getattr(detection, "identity", None)
            unverified_reid = face_det and (not identity or identity.lower() in ["unknown", "unidentified"])

            # Speed
            speed = getattr(detection, "speed_kmh", 0) or 0
            high_speed = speed > 25.0

            result = self.engine.evaluate(
                night_period=is_night,
                restricted_zone=is_restricted,
                loitering=is_loitering,
                degraded_footage=is_degraded,
                unverified_reid=unverified_reid,
                high_speed_movement=high_speed,
            )

            detection.risk_score = result["score"]
            detection.risk_level = result["risk_level"]
            detection.alert = result["is_suspicious"]
            detection.reasons = [f["label"] for f in result["contributing_factors"]]
            detection.contributing_factors = result["contributing_factors"]

        return packet