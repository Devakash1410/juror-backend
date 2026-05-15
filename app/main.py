"""
FastAPI application entry point for JUROR backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routes import jury
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="JUROR - AI Hallucination Oversight System",
    description="Multi-agent AI verification and correction system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jury.router)


@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("JUROR Backend starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger.info("JUROR Backend shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "JUROR - AI Hallucination Oversight System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "health": "GET /api/v1/health",
            "websocket": "WS /api/v1/ws/jury/{analysis_id}",
            "stream": "GET /api/v1/stream/analyze"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
