from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
@router.get("/")
async def root():
    return {
        "project": "SentinelAI",
        "status": "running"
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }