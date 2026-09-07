"""
Analytics API Routes

GET /analytics/summary — high-level detection and track metrics
GET /analytics/hourly  — timeline distribution of detections
"""

from fastapi import APIRouter
from database.repository import Repository

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

repo = Repository()


@router.get("/summary")
async def summary():
    try:
        raw_tracks = repo.get_tracks()
    except Exception:
        raw_tracks = []

    tracks = [dict(t) if not isinstance(t, dict) else t for t in raw_tracks]

    people = len([t for t in tracks if t.get("class_name") == "person"])
    vehicles = len([t for t in tracks if t.get("class_name") in ["car", "truck", "bus", "motorcycle", "vehicle"]])
    other = len(tracks) - people - vehicles

    return {
        "total_tracks": len(tracks),
        "people": people,
        "vehicles": vehicles,
        "other": max(0, other),
    }


@router.get("/hourly")
async def hourly_activity():
    try:
        raw_tracks = repo.get_tracks()
    except Exception:
        raw_tracks = []

    tracks = [dict(t) if not isinstance(t, dict) else t for t in raw_tracks]

    hours = [f"{h:02d}:00" for h in range(24)]
    counts = [0] * 24

    for t in tracks:
        ts = str(t.get("timestamp", ""))
        if " " in ts and ":" in ts:
            time_part = ts.split(" ")[1]
            try:
                hour = int(time_part.split(":")[0])
                if 0 <= hour < 24:
                    counts[hour] += 1
            except ValueError:
                pass

    return [{"hour": h, "detections": c} for h, c in zip(hours, counts)]
