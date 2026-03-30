"""
Search API routes
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.moviebox_service import MovieBoxService
from app.models import SearchResponse

router = APIRouter()
service = MovieBoxService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/search", response_model=SearchResponse)
@limiter.limit("10/minute")  # Search is resource intensive, limit more
async def search_movies(
    request: Request,
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query("ALL", description="Subject type: ALL, MOVIES, TV_SERIES"),
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(24, description="Items per page", ge=1, le=100)
):
    """
    Search for movies and TV series

    - **q**: Search query (required)
    - **type**: Filter by type (ALL, MOVIES, TV_SERIES)
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 24, max: 100)
    """
    result = await service.search(q, type, page, per_page)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result