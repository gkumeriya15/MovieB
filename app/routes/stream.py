"""
Stream API routes
"""

from fastapi import APIRouter, HTTPException, Path, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.moviebox_service import MovieBoxService
from app.models import StreamResponse

router = APIRouter()
service = MovieBoxService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/stream/{page_url:path}", response_model=StreamResponse)
@limiter.limit("10/minute")  # Streaming links are sensitive, limit more
async def get_stream_links(
    request: Request,
    page_url: str = Path(
        ..., 
        description="Item identifier (page_url or numeric id). Example: /detail/xyz?id=... or 332588..."
    )
):
    """
    Get streaming/download links for a movie

    - **page_url**: Item page URL identifier from search results
    """
    result = await service.get_stream_links(page_url)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/stream/episode/{episode_id}", response_model=StreamResponse)
@limiter.limit("10/minute")  # Streaming links are sensitive, limit more
async def get_episode_stream_links(
    request: Request,
    episode_id: str = Path(
        ..., 
        description="Episode identifier in format s{season}e{episode}. Example: s1e1"
    ),
    page_url: str = Query(
        ..., 
        description="TV series page URL identifier. Example: /detail/xyz?id=... or 332588..."
    )
):
    """
    Get streaming/download links for a specific TV series episode

    - **episode_id**: Episode identifier (e.g., s1e1 for season 1 episode 1)
    - **page_url**: TV series page URL identifier (query parameter)
    """
    result = await service.get_episode_stream_links(page_url, episode_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result