"""
SentinelAI Risk Evaluation API Routes

GET  /risk/{track_id} — Retrieve rule-based risk evaluation for a track
POST /risk/evaluate   — Evaluate custom indicators with transparent contributing factors
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.suspicion_agent import RuleBasedRiskEngine
from database.repository import Repository

router = APIRouter(
    prefix="/risk",
    tags=["Risk Engine"],
)

_repo = Repository()
_engine = RuleBasedRiskEngine()


class RiskEvaluationRequest(BaseModel):
    night_period: bool = False
    restricted_zone: bool = False
    loitering: bool = False
    degraded_footage: bool = False
    unverified_reid: bool = False
    high_speed_movement: bool = False
    metadata: Optional[Dict[str, Any]] = None


@router.post("/evaluate")
async def evaluate_risk(payload: RiskEvaluationRequest):
    """
    Evaluate surveillance parameters against deterministic risk factors.

    Returns:
    - composite risk score (0-100)
    - risk level (Low, Medium, High, Critical)
    - transparent contributing factors breakdown with weights
    """
    result = _engine.evaluate(
        night_period=payload.night_period,
        restricted_zone=payload.restricted_zone,
        loitering=payload.loitering,
        degraded_footage=payload.degraded_footage,
        unverified_reid=payload.unverified_reid,
        high_speed_movement=payload.high_speed_movement,
        metadata=payload.metadata,
    )
    return {
        "composite_score": result["score"],
        **result,
    }


@router.get("/{track_id}")
async def get_track_risk(track_id: int):
    """
    Retrieve rule-based risk evaluation and contributing factors for a specific track.
    """
    try:
        track = _repo.get_track(track_id)
        if not track:
            raise HTTPException(status_code=404, detail=f"Track ID {track_id} not found.")

        events = _repo.get_events(track_id)
        faces = _repo.get_face(track_id)

        # Determine indicators from records
        is_blurry = bool(track.get("is_blurry", 0))
        quality_score = float(track.get("quality_score", 100.0))
        degraded = is_blurry or (quality_score < 40.0)

        has_face = bool(track.get("face_detected", 0))
        unverified = has_face and len(faces) == 0

        event_names = [str(e.get("event", "")).lower() for e in events]
        restricted = any("intrusion" in ev or "restricted" in ev or "fence" in ev for ev in event_names)
        loitering = any("loitering" in ev or "dwell" in ev for ev in event_names)
        night = any("night" in ev for ev in event_names)

        result = _engine.evaluate(
            night_period=night,
            restricted_zone=restricted,
            loitering=loitering,
            degraded_footage=degraded,
            unverified_reid=unverified,
            high_speed_movement=False,
            metadata={"track_id": track_id, "event_count": len(events)},
        )
        return {
            "track_id": track_id,
            "composite_score": result["score"],
            **result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating track risk: {str(e)}")

