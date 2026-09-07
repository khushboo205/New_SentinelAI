"""
Events API Routes

GET /events        — list events from database
GET /events/{id}   — get single event detail
"""

from fastapi import APIRouter, HTTPException, Query

from database.repository import Repository

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

_repo = Repository()


@router.get("/")
async def list_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all events from the database."""
    try:
        events = _repo.list_events(limit=limit, offset=offset)
        return {
            "count": len(events),
            "events": events,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/summary")
async def events_summary():
    """Return high-level event counts."""
    try:
        total = _repo.count_events()
        suspicious = _repo.count_risk()
        tracks = _repo.count_tracks()
        faces = _repo.count_faces()
        return {
            "total_events": total,
            "suspicious_tracks": suspicious,
            "total_tracks": tracks,
            "faces_detected": faces,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{event_id}")
async def get_event(event_id: int):
    """Get a single event by ID."""
    try:
        event = _repo.get_event_by_id(event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
