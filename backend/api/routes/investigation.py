from fastapi import APIRouter
from services.investigation_service import InvestigationService
from fastapi import HTTPException

router = APIRouter(
    prefix="/investigation",
    tags=["Investigation"]
)

service = InvestigationService()


# Returns all tracks
@router.get("/")
async def list_tracks():
    return service.get_tracks()


# Returns investigation details of one track
@router.get("/{track_id}")
async def get_investigation(track_id: int):

    result = service.get_investigation(track_id)

    if result["track"] is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found"
        )

    return {
        "success": True,
        "data": result
    }
@router.get("/summary/stats")
async def stats():
    return {
        "tracks": len(service.get_tracks())
    }


from pydantic import BaseModel


class TimelineEventRequest(BaseModel):
    event: str


@router.post("/{track_id}/timeline")
async def add_timeline_event(track_id: int, payload: TimelineEventRequest):
    track = service.repository.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    service.repository.save_timeline(track_id, payload.event)
    return {
        "success": True,
        "message": f"Timeline event logged for Track #{track_id}",
    }