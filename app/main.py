"""
FastAPI application for MovieBox API
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn

from app.routes.search import router as search_router
from app.routes.details import router as details_router
from app.routes.episodes import router as episodes_router
from app.routes.stream import router as stream_router
from app.services.moviebox_service import MovieBoxService
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager"""
    # Startup
    setup_logging()
    yield
    # Shutdown


app = FastAPI(
    title="MovieBox API",
    description="REST API for MovieBox - search, discover and stream movies and TV series",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (optional, for production)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )


@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "service": "MovieBox API"
    }


# Include routers
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(details_router, prefix="/api/v1", tags=["details"])
app.include_router(episodes_router, prefix="/api/v1", tags=["episodes"])
app.include_router(stream_router, prefix="/api/v1", tags=["stream"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )