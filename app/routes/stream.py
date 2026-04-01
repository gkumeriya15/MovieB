"""
Stream API routes with enhanced error handling and documentation
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
    
    Formats accepted:
    - Full URL: https://moviebox.ph/detail/slug-name?id=123456
    - Relative URL: /detail/slug-name?id=123456
    - Numeric ID: 123456
    """
    result = await service.get_stream_links(page_url)

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Failed to get stream links")
        )

    return result


@router.get("/stream/episode/{episode_id}", response_model=StreamResponse)
@limiter.limit("10/minute")  # Streaming links are sensitive, limit more
async def get_episode_stream_links(
    request: Request,
    episode_id: str = Path(
        ..., 
        description="Episode identifier in format s{season}e{episode}. Example: s1e1, s2e5, s10e12"
    ),
    page_url: str = Query(
        ..., 
        description="TV series page URL identifier. Formats: https://moviebox.ph/detail/slug?id=123 or /detail/slug?id=123 or numeric ID"
    )
):
    """
    Get streaming/download links for a specific TV series episode
    
    **Episode Mapping:**
    - s1e1 = Season 1, Episode 1
    - s2e5 = Season 2, Episode 5
    - s10e12 = Season 10, Episode 12

    **page_url Parameter:**
    Accepts multiple formats:
    - Full URL: https://moviebox.ph/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440
    - Relative URL: /detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440
    - Numeric ID: 5203417860348986440

    **Features:**
    - URL normalization for flexible input formats
    - Token expiration detection in stream URLs
    - Automatic stream caching for 30 minutes
    - Detailed expiration timestamps in response
    - Warning for expired streams
    
    **Response Example:**
    ```json
    {
      "success": true,
      "data": {
        "id": "5203417860348986440",
        "title": "Boyfriend on Demand",
        "type": "tv_series",
        "episode_id": "s1e2",
        "season": 1,
        "episode": 2,
        "streams": [
          {
            "quality": "1080p",
            "url": "https://example.com/video.mp4?sign=xxx&t=1234567890",
            "size": 2147483648,
            "format": "mp4",
            "file_size_human": "2.0 GB",
            "expires_in_seconds": 86400,
            "expires_at": 1704067200
          }
        ],
        "best_quality": "1080p"
      }
    }
    ```
    
    **Error Cases:**
    - Invalid episode_id format (not matching s{season}e{episode})
    - Invalid page_url format
    - Item not found
    - Item is a movie, not a TV series
    - No streams available for episode
    """
    result = await service.get_episode_stream_links(page_url, episode_id)

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result.get("error", f"Failed to get stream links for episode {episode_id}")
        )

    return result