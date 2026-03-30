"""
Pydantic models for API responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl


class SearchItem(BaseModel):
    """Model for search result item"""
    id: str
    title: str
    subject_type: str
    release_date: Optional[str] = None
    genre: List[str]
    country: str
    imdb_rating: float
    cover: Optional[Dict[str, str]] = None
    page_url: str


class Pagination(BaseModel):
    """Model for pagination info"""
    page: int
    per_page: int
    has_more: bool
    total: Optional[int] = None


class SearchResponse(BaseModel):
    """Model for search API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DetailsResponse(BaseModel):
    """Model for details API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class EpisodesResponse(BaseModel):
    """Model for episodes API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StreamResponse(BaseModel):
    """Model for stream API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Model for health check response"""
    success: bool
    status: str
    service: str