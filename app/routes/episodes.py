"""
Episodes API routes
"""

from fastapi import APIRouter, HTTPException, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.moviebox_service import MovieBoxService
from app.models import EpisodesResponse

router = APIRouter()
service = MovieBoxService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/episodes/{page_url:path}", response_model=EpisodesResponse)
@limiter.limit("15/minute")
async def get_tv_episodes(
    request: Request,
    page_url: str = Path(..., description="TV series page URL identifier")
):
    """
    Get episodes for a TV series

    - **page_url**: TV series page URL identifier from search results
    """
    result = await service.get_episodes(page_url)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result