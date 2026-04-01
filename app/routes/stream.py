"""
Stream API routes
"""

from fastapi import APIRouter, HTTPException, Path, Request
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
    Get streaming/download links for a movie or TV series

    - **page_url**: Item page URL identifier from search results
    """
    result = await service.get_stream_links(page_url)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result