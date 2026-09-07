from fastapi import APIRouter
from services.pipeline_service import PipelineService

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"]
)

service = PipelineService()

@router.post("/run")
async def run_pipeline():

    return service.run()