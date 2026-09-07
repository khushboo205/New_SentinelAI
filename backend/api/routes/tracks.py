from fastapi import APIRouter
from services.investigation_service import InvestigationService

router = APIRouter(prefix="/tracks", tags=["Tracks"])

service = InvestigationService()


@router.get("/{track_id}")
async def get_track(track_id: int):

    return service.get_investigation(track_id)