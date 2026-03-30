"""
MovieBox service layer - wraps the existing moviebox-api logic
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from moviebox_api.v1.core import Search, MovieDetails, TVSeriesDetails
from moviebox_api.v1.constants import SubjectType
from moviebox_api.v1.models import SearchResultsModel
from moviebox_api.v1.extractor.models.json import ItemJsonDetailsModel
from moviebox_api.v1.requests import Session
from moviebox_api.v1.download import DownloadableMovieFilesDetail, DownloadableTVSeriesFilesDetail
from moviebox_api.v1.exceptions import MovieboxApiException

from app.utils.logger import get_logger


logger = get_logger(__name__)


class MovieBoxService:
    """Service layer for MovieBox API operations"""

    def __init__(self):
        self._session: Optional[Session] = None

    @asynccontextmanager
    async def _get_session(self) -> Session:
        """Get or create a session for the current operation"""
        if self._session is None:
            self._session = Session()

        try:
            yield self._session
        except Exception as e:
            logger.error(f"Session error: {e}")
            # Reset session on error
            self._session = None
            raise

    async def search(
        self,
        query: str,
        subject_type: str = "ALL",
        page: int = 1,
        per_page: int = 24
    ) -> Dict[str, Any]:
        """Search for movies and TV series"""
        try:
            # Map string to SubjectType enum
            subject_type_enum = getattr(SubjectType, subject_type.upper(), SubjectType.ALL)

            async with self._get_session() as session:
                search = Search(
                    session=session,
                    query=query,
                    subject_type=subject_type_enum,
                    page=page,
                    per_page=per_page
                )

                content = await search.get_content()
                model = await search.get_content_model()

                return {
                    "success": True,
                    "data": {
                        "items": [
                            {
                                "id": item.subjectId,
                                "title": item.title,
                                "subject_type": item.subjectType.value,
                                "release_date": item.releaseDate.isoformat() if item.releaseDate else None,
                                "genre": item.genre,
                                "country": item.countryName,
                                "imdb_rating": item.imdbRatingValue,
                                "cover": {
                                    "url": str(item.cover.url),
                                    "thumbnail": item.cover.thumbnail
                                } if item.cover else None,
                                "page_url": item.page_url
                            }
                            for item in model.items
                        ],
                        "pagination": {
                            "page": model.pager.page,
                            "per_page": model.pager.perPage,
                            "has_more": model.pager.hasMore,
                            "total": model.pager.total if hasattr(model.pager, 'total') else None
                        }
                    }
                }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_details(self, page_url: str) -> Dict[str, Any]:
        """Get detailed information about a movie or TV series"""
        try:
            async with self._get_session() as session:
                # page_url should be something like "detail/naruto-hindi-8iXhwtr47c5?id=4360485895745717992"
                # The moviebox-api expects the full relative path starting with /detail/
                full_page_url = page_url if page_url.startswith('/') else f"/{page_url}"

                # Try movie first, then TV series - both might work but we check the actual type
                try:
                    details = MovieDetails(full_page_url, session)
                    model = await details.get_content_model()
                    item_type = "movie" if model.resData.subject.subjectType.value == 1 else "tv_series"
                except Exception:
                    # Try TV series
                    try:
                        details = TVSeriesDetails(full_page_url, session)
                        model = await details.get_content_model()
                        item_type = "tv_series"
                    except Exception as tv_error:
                        raise ValueError(f"Could not find item with page URL: {page_url}. TV error: {str(tv_error)}")

                return {
                    "success": True,
                    "data": {
                        "id": model.resData.subject.subjectId,
                        "title": model.resData.subject.title,
                        "description": model.resData.subject.description,
                        "release_date": model.resData.subject.releaseDate.isoformat() if model.resData.subject.releaseDate else None,
                        "duration": model.resData.subject.duration,
                        "genre": model.resData.subject.genre,
                        "country": model.resData.subject.countryName,
                        "imdb_rating": model.resData.subject.imdbRatingValue,
                        "cover": {
                            "url": str(model.resData.subject.cover.url),
                            "thumbnail": model.resData.subject.cover.thumbnail
                        } if model.resData.subject.cover else None,
                        "trailer": {
                            "url": str(model.resData.subject.trailer.videoAddress.url) if model.resData.subject.trailer and model.resData.subject.trailer.videoAddress else None
                        } if model.resData.subject.trailer else None,
                        "type": item_type
                    }
                }

        except Exception as e:
            logger.error(f"Details error for {page_url}: {e}")
            return {
                "success": False,
                "error": f"Failed to get details for {page_url}: {str(e)}"
            }

    async def get_episodes(self, page_url: str) -> Dict[str, Any]:
        """Get episodes for a TV series"""
        try:
            async with self._get_session() as session:
                # First get the item details to determine type
                details_result = await self.get_details(page_url)
                if not details_result["success"]:
                    return details_result

                item_data = details_result["data"]
                if item_data["type"] != "tv_series":
                    return {
                        "success": False,
                        "error": f"Item {page_url} is not a TV series (type: {item_data['type']})"
                    }

                # Construct the full page URL
                full_page_url = page_url if page_url.startswith('/') else f"/{page_url}"

                details = TVSeriesDetails(full_page_url, session)
                model = await details.get_content_model()

                episodes = []
                if hasattr(model, 'resData') and hasattr(model.resData, 'postList') and model.resData.postList:
                    for season in model.resData.postList:
                        if hasattr(season, 'episodes') and season.episodes:
                            for episode in season.episodes:
                                episodes.append({
                                    "id": getattr(episode, 'id', f"s{season.season}e{episode.episode}"),
                                    "title": getattr(episode, 'title', f"Episode {episode.episode}"),
                                    "episode_number": getattr(episode, 'episode', 0),
                                    "season_number": getattr(season, 'season', 0),
                                    "duration": getattr(episode, 'duration', 0),
                                    "release_date": episode.releaseDate.isoformat() if hasattr(episode, 'releaseDate') and episode.releaseDate else None
                                })

                return {
                    "success": True,
                    "data": {
                        "id": item_data["id"],
                        "title": item_data["title"],
                        "total_episodes": len(episodes),
                        "episodes": episodes
                    }
                }

        except Exception as e:
            logger.error(f"Episodes error for {page_url}: {e}")
            return {
                "success": False,
                "error": f"Failed to get episodes for {page_url}: {str(e)}"
            }

    async def get_stream_links(self, page_url: str) -> Dict[str, Any]:
        """Get streaming/download links for a movie or TV series"""
        try:
            async with self._get_session() as session:
                # Construct the full page URL
                full_page_url = page_url if page_url.startswith('/') else f"/{page_url}"

                # Try movie first, then TV series - both might work but we check the actual type
                try:
                    details = MovieDetails(full_page_url, session)
                    model = await details.get_content_model()
                    item_type = "movie" if model.resData.subject.subjectType.value == 1 else "tv_series"
                    downloader = DownloadableMovieFilesDetail(session, model) if item_type == "movie" else DownloadableTVSeriesFilesDetail(session, model)
                except Exception:
                    # Try TV series
                    try:
                        details = TVSeriesDetails(full_page_url, session)
                        model = await details.get_content_model()
                        item_type = "tv_series"
                        downloader = DownloadableTVSeriesFilesDetail(session, model)
                    except Exception as tv_error:
                        raise ValueError(f"Could not find item with page URL: {page_url}. TV error: {str(tv_error)}")

                try:
                    # For movies, use the parameterless get_content_model
                    # For TV series, we'd need season/episode, but for now get general info
                    if item_type == "movie":
                        metadata = await downloader.get_content_model()
                    else:
                        # For TV series, try to get download info for first episode
                        try:
                            metadata = await downloader.get_content_model(1, 1)
                        except Exception:
                            # If episode-specific fails, return empty streams for now
                            return {
                                "success": True,
                                "data": {
                                    "id": model.resData.subject.subjectId,
                                    "title": model.resData.subject.title,
                                    "type": item_type,
                                    "streams": [],
                                    "best_quality": None,
                                    "message": "Streaming links not available for this TV series. Try episode-specific endpoints."
                                }
                            }

                    # Check if downloads are available
                    if not hasattr(metadata, 'downloads') or not metadata.downloads:
                        return {
                            "success": True,
                            "data": {
                                "id": model.resData.subject.subjectId,
                                "title": model.resData.subject.title,
                                "type": item_type,
                                "streams": [],
                                "best_quality": None,
                                "message": "No streaming links available for this item."
                            }
                        }

                    # Check if downloads are available
                    if not hasattr(metadata, 'downloads') or not metadata.downloads:
                        return {
                            "success": True,
                            "data": {
                                "id": model.resData.subject.subjectId,
                                "title": model.resData.subject.title,
                                "type": item_type,
                                "streams": [],
                                "best_quality": None,
                                "message": "No streaming links available for this item."
                            }
                        }

                    streams = []
                    quality_map = metadata.get_quality_downloads_map()
                    for quality, file_info in quality_map.items():
                        streams.append({
                            "quality": quality,
                            "url": str(file_info.url),
                            "size": getattr(file_info, 'size', 0),
                            "format": getattr(file_info, 'format', 'unknown'),
                            "file_size_human": getattr(file_info, 'get_file_size_human', lambda: 'Unknown')()
                        })

                    # Get best quality safely
                    try:
                        best_quality = metadata.best_media_file.quality if metadata.downloads else None
                    except Exception:
                        best_quality = None

                    return {
                        "success": True,
                        "data": {
                            "id": model.resData.subject.subjectId,
                            "title": model.resData.subject.title,
                            "type": item_type,
                            "streams": streams,
                            "best_quality": best_quality
                        }
                    }

                except Exception as download_error:
                    logger.warning(f"Download metadata error for {page_url}: {download_error}")
                    # Return success with empty streams instead of error
                    return {
                        "success": True,
                        "data": {
                            "id": model.resData.subject.subjectId if 'model' in locals() else "unknown",
                            "title": model.resData.subject.title if 'model' in locals() else "unknown",
                            "type": item_type if 'item_type' in locals() else "unknown",
                            "streams": [],
                            "best_quality": None,
                            "message": f"Streaming links not available: {str(download_error)}"
                        }
                    }

        except Exception as e:
            logger.error(f"Stream links error for {page_url}: {e}")
            return {
                "success": False,
                "error": f"Failed to get stream links for {page_url}: {str(e)}"
            }