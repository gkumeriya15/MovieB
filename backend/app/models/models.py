"""
Database models for the streaming platform
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.dialects.sqlite import JSON
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class ContentType(str, enum.Enum):
    """Content types"""
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    ANIME = "anime"
    LIVE_STREAM = "live_stream"


class VideoFormat(str, enum.Enum):
    """Supported video formats"""
    HLS = "hls"  # m3u8
    MP4 = "mp4"
    MKV = "mkv"
    HTTP = "http"
    RTMP = "rtmp"
    YOUTUBE = "youtube"


# Association table for many-to-many relationships
user_watchlist = Table(
    'user_watchlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    Column('content_id', Integer, ForeignKey('content.id', ondelete='CASCADE'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow),
)

content_genres = Table(
    'content_genres',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True),
)

content_categories = Table(
    'content_categories',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id', ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    """User model"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # None if OAuth login
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    watch_history = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("Content", secondary=user_watchlist, backref="added_to_watchlist_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    content_requests = relationship("ContentRequest", back_populates="requested_by", cascade="all, delete-orphan")


class Content(Base):
    """Media content (movies, TV shows, anime)"""
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True, nullable=False)
    slug = Column(String(500), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)  # movie, tv_show, anime, live_stream
    poster_url = Column(String(500), nullable=True)
    background_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)
    tmdb_id = Column(String(255), nullable=True, index=True)
    imdb_id = Column(String(255), nullable=True, index=True)
    rating = Column(Float, nullable=True)  # IMDb rating
    release_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # For movies
    language = Column(String(50), default="en", nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    genres = relationship("Genre", secondary=content_genres, backref="contents")
    categories = relationship("Category", secondary=content_categories, backref="contents")
    videos = relationship("Video", back_populates="content", cascade="all, delete-orphan")
    episodes = relationship("Episode", back_populates="content", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="content", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="content", cascade="all, delete-orphan")
    subtitles = relationship("Subtitle", back_populates="content", cascade="all, delete-orphan")


class Episode(Base):
    """Episode for TV shows and anime"""
    __tablename__ = "episode"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    air_date = Column(DateTime, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("Content", back_populates="episodes")
    videos = relationship("Video", back_populates="episode", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="episode", cascade="all, delete-orphan")


class Video(Base):
    """Video stream source"""
    __tablename__ = "video"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episode.id", ondelete="CASCADE"), nullable=True)
    format = Column(Enum(VideoFormat), nullable=False)  # hls, mp4, mkv, http, rtmp, youtube
    quality_label = Column(String(50), nullable=True)  # 360p, 720p, 1080p, 4K, etc.
    url = Column(String(1000), nullable=False)
    source_name = Column(String(255), nullable=True)  # e.g., "VidCloud", "Direct Upload", etc.
    is_default = Column(Boolean, default=False, nullable=False)
    size_mb = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("Content", back_populates="videos")
    episode = relationship("Episode", back_populates="videos")


class Subtitle(Base):
    """Subtitle track"""
    __tablename__ = "subtitle"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episode.id", ondelete="CASCADE"), nullable=True)
    language = Column(String(50), nullable=False)  # e.g., "en", "es", "fr"
    language_name = Column(String(100), nullable=True)  # e.g., "English"
    url = Column(String(1000), nullable=False)
    format = Column(String(20), default="vtt", nullable=False)  # srt, vtt, ass, etc.
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("Content", back_populates="subtitles")


class WatchHistory(Base):
    """User watch history"""
    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episode.id", ondelete="CASCADE"), nullable=True)
    duration_watched = Column(Integer, nullable=True)  # In seconds
    last_watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="watch_history")
    content = relationship("Content", back_populates="watch_history")
    episode = relationship("Episode", back_populates="watch_history")


class Genre(Base):
    """Genre"""
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)


class Category(Base):
    """Content category"""
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)


class Comment(Base):
    """User comments on content"""
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    likes = Column(Integer, default=0, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    content = relationship("Content", back_populates="comments")


class Notification(Base):
    """User notifications"""
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # new_episode, new_content, system, etc.
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class ContentRequest(Base):
    """User content requests"""
    __tablename__ = "content_request"

    id = Column(Integer, primary_key=True, index=True)
    requested_by_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    request_type = Column(Enum(ContentType), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    requested_by = relationship("User", back_populates="content_requests")


class Advertisement(Base):
    """Advertisement/Ads"""
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ad_type = Column(String(50), nullable=False)  # banner, popup, video, etc.
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    target_url = Column(String(500), nullable=True)
    placement = Column(String(50), nullable=False)  # homepage, player, sidebar, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class HomePage(Base):
    """Homepage configuration for customizable sections"""
    __tablename__ = "home_page"

    id = Column(Integer, primary_key=True, index=True)
    section_name = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    section_type = Column(String(50), nullable=False)  # slider, grid, featured, trending, etc.
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional config data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SystemSetting(Base):
    """System settings for admin configuration"""
    __tablename__ = "system_setting"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)  # string, integer, boolean, json
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
