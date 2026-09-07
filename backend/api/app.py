from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes.pipeline import router as pipeline_router
from api.routes.upload import router as upload_router
from api.routes.investigation import router as investigation_router
from api.routes.health import router as health_router
from api.routes.tracks import router as tracks_router
from api.routes.enhancement import router as enhancement_router
from api.routes.events import router as events_router
from api.routes.system import router as system_router
from api.routes.analytics import router as analytics_router
from api.routes.risk import router as risk_router
from api.routes.cameras import router as cameras_router
from api.routes.evidence import router as evidence_router
from api.routes.reports import router as reports_router
from database.schema import Schema

logger = logging.getLogger("SentinelAI.API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema & indexes exist
    try:
        schema = Schema()
        schema.create_tables()
        logger.info("SentinelAI database initialized successfully.")
    except Exception as exc:
        logger.error(f"Failed to initialize database schema: {exc}")
    yield
    # Shutdown logic if any


app = FastAPI(
    title="SentinelAI — Quality-Aware Vision Engine",
    description="IBVAP backend: quality analysis, adaptive enhancement, detection, tracking, investigation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error occurred.",
                "detail": str(exc),
            },
        },
    )


# Register routers both directly and with /api prefix for proxy resilience
routers = [
    health_router,
    upload_router,
    investigation_router,
    pipeline_router,
    tracks_router,
    enhancement_router,
    events_router,
    system_router,
    analytics_router,
    risk_router,
    cameras_router,
    evidence_router,
    reports_router,
]

for r in routers:
    app.include_router(r)
    app.include_router(r, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    return {
        "platform": "IBVAP — Intelligent Border Video Analytics Platform",
        "engine": "SentinelAI Quality-Aware Vision Engine",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }