"""
Pydantic schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============================================
# User Schemas
# ============================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response"""
    updated_at: datetime


# ============================================
# Authentication Schemas
# ============================================

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None


# ============================================
# Content Schemas
# ============================================

class GenreSchema(BaseModel):
    """Genre schema"""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class CategorySchema(BaseModel):
    """Category schema"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class VideoSchema(BaseModel):
    """Video schema"""
    id: int
    format: str
    quality_label: Optional[str] = None
    url: str
    source_name: Optional[str] = None
    is_default: bool

    class Config:
        from_attributes = True


class SubtitleSchema(BaseModel):
    """Subtitle schema"""
    id: int
    language: str
    language_name: Optional[str] = None
    url: str
    format: str
    is_default: bool

    class Config:
        from_attributes = True


class EpisodeSchema(BaseModel):
    """Episode schema"""
    id: int
    season_number: int
    episode_number: int
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    air_date: Optional[datetime] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


class ContentBase(BaseModel):
    """Base content schema"""
    title: str
    description: Optional[str] = None
    content_type: str
    poster_url: Optional[str] = None
    background_url: Optional[str] = None
    trailer_url: Optional[str] = None
    release_date: Optional[datetime] = None
    language: str = "en"


class ContentCreate(ContentBase):
    """Content creation schema"""
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    rating: Optional[float] = None
    duration_minutes: Optional[int] = None


class ContentResponse(ContentBase):
    """Content response schema"""
    id: int
    slug: str
    rating: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_featured: bool
    is_active: bool
    view_count: int
    created_at: datetime
    genres: List[GenreSchema] = []
    categories: List[CategorySchema] = []

    class Config:
        from_attributes = True


class ContentDetailResponse(ContentResponse):
    """Detailed content response"""
    videos: List[VideoSchema] = []
    subtitles: List[SubtitleSchema] = []
    episodes: List[EpisodeSchema] = []
    updated_at: datetime


# ============================================
# Watch History & Watchlist Schemas
# ============================================

class WatchHistoryCreate(BaseModel):
    """Watch history creation"""
    duration_watched: Optional[int] = None
    is_completed: bool = False


class WatchHistoryResponse(BaseModel):
    """Watch history response"""
    id: int
    content_id: int
    episode_id: Optional[int] = None
    duration_watched: Optional[int] = None
    last_watched_at: datetime
    is_completed: bool

    class Config:
        from_attributes = True


class WatchlistResponse(BaseModel):
    """Watchlist response"""
    id: int
    content: ContentResponse
    added_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Comments & Notifications Schemas
# ============================================

class CommentCreate(BaseModel):
    """Comment creation"""
    text: str
    rating: Optional[int] = Field(None, ge=1, le=5)


class CommentResponse(BaseModel):
    """Comment response"""
    id: int
    user: UserResponse
    text: str
    rating: Optional[int] = None
    likes: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Content Request Schemas
# ============================================

class ContentRequestCreate(BaseModel):
    """Content request creation"""
    title: str
    request_type: str
    description: Optional[str] = None


class ContentRequestResponse(BaseModel):
    """Content request response"""
    id: int
    title: str
    request_type: str
    description: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Search & Filter Schemas
# ============================================

class SearchQuery(BaseModel):
    """Search query parameters"""
    q: str = Field(..., min_length=1, max_length=255)
    content_type: Optional[str] = None
    genre_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    year: Optional[int] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "relevance"  # relevance, rating, date, popularity


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    total: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool
    data: List


# ============================================
# Admin Schemas
# ============================================

class SystemSettingResponse(BaseModel):
    """System setting response"""
    id: int
    key: str
    value: str
    setting_type: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class HomePageSectionResponse(BaseModel):
    """Homepage section response"""
    id: int
    section_name: str
    title: str
    description: Optional[str] = None
    section_type: str
    order: int
    is_active: bool
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
