"""
Details API routes
"""

from fastapi import APIRouter, HTTPException, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.moviebox_service import MovieBoxService
from app.models import DetailsResponse

router = APIRouter()
service = MovieBoxService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/details/{page_url:path}", response_model=DetailsResponse)
@limiter.limit("20/minute")
async def get_item_details(
    request: Request,
    page_url: str = Path(
        ..., 
        description="Item identifier (page_url or numeric id). Example page_url: /detail/naruto-2D7JgAQBGX3?id=3325889774849773352"
    )
):
    """
    Get detailed information about a movie or TV series

    - **page_url**: Page URL identifier from search results
    """
    result = await service.get_details(page_url)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result