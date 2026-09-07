from pydantic import BaseModel
from typing import List, Optional


class TrackResponse(BaseModel):
    track_id: int
    class_name: str


class InvestigationResponse(BaseModel):
    track: dict | None
    events: List[dict]
    features: List[dict]
    faces: List[dict]
    ocr: List[dict]
    risk: List[dict]