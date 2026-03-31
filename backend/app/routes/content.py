"""
Content routes (movies, TV shows, anime)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Content, User, WatchHistory, Genre, Category
from app.schemas import ContentResponse, ContentDetailResponse, SearchQuery
from app.routes.auth import get_current_user

router = APIRouter(prefix="/content", tags=["Content"])


# ============================================
# Search & Browse
# ============================================

@router.get("/movies", response_model=List[ContentResponse])
async def list_movies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|rating|view_count)$"),
    db: Session = Depends(get_db),
):
    """Get list of movies"""
    query = db.query(Content).filter(Content.content_type == "movie", Content.is_active == True)
    
    # Sort
    if sort_by == "rating":
        query = query.order_by(Content.rating.desc())
    elif sort_by == "view_count":
        query = query.order_by(Content.view_count.desc())
    else:
        query = query.order_by(Content.created_at.desc())
    
    # Pagination
    skip = (page - 1) * limit
    contents = query.offset(skip).limit(limit).all()
    
    return contents


@router.get("/tv-shows", response_model=List[ContentResponse])
async def list_tv_shows(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get list of TV shows"""
    query = db.query(Content).filter(Content.content_type == "tv_show", Content.is_active == True)
    query = query.order_by(Content.created_at.desc())
    
    skip = (page - 1) * limit
    contents = query.offset(skip).limit(limit).all()
    
    return contents


@router.get("/anime", response_model=List[ContentResponse])
async def list_anime(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get list of anime"""
    query = db.query(Content).filter(Content.content_type == "anime", Content.is_active == True)
    query = query.order_by(Content.created_at.desc())
    
    skip = (page - 1) * limit
    contents = query.offset(skip).limit(limit).all()
    
    return contents


@router.get("/featured", response_model=List[ContentResponse])
async def get_featured_content(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Get featured/homepage content"""
    contents = db.query(Content).filter(
        Content.is_featured == True,
        Content.is_active == True
    ).order_by(Content.created_at.desc()).limit(limit).all()
    
    return contents


@router.get("/trending", response_model=List[ContentResponse])
async def get_trending_content(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Get trending content"""
    contents = db.query(Content).filter(
        Content.is_active == True
    ).order_by(Content.view_count.desc()).limit(limit).all()
    
    return contents


@router.get("/search", response_model=List[ContentResponse])
async def search_content(
    q: str = Query(..., min_length=1),
    content_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search content"""
    query = db.query(Content).filter(
        Content.title.ilike(f"%{q}%"),
        Content.is_active == True
    )
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    query = query.order_by(Content.created_at.desc())
    
    skip = (page - 1) * limit
    contents = query.offset(skip).limit(limit).all()
    
    return contents


# ============================================
# Content Details
# ============================================

@router.get("/{content_id}", response_model=ContentDetailResponse)
async def get_content_details(
    content_id: int,
    db: Session = Depends(get_db),
):
    """Get content details"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Increment view count
    content.view_count += 1
    db.add(content)
    db.commit()
    
    return content


# ============================================
# User Watchlist & History
# ============================================

@router.post("/{content_id}/add-to-watchlist")
async def add_to_watchlist(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add content to user watchlist"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already in watchlist
    if content in current_user.watchlist:
        raise HTTPException(
            status_code=400,
            detail="Content already in watchlist"
        )
    
    current_user.watchlist.append(content)
    db.add(current_user)
    db.commit()
    
    return {"message": "Added to watchlist"}


@router.delete("/{content_id}/remove-from-watchlist")
async def remove_from_watchlist(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove content from watchlist"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content not in current_user.watchlist:
        raise HTTPException(
            status_code=400,
            detail="Content not in watchlist"
        )
    
    current_user.watchlist.remove(content)
    db.add(current_user)
    db.commit()
    
    return {"message": "Removed from watchlist"}


@router.get("/user/watchlist")
async def get_user_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's watchlist"""
    # Refresh to get latest relationships
    db.refresh(current_user)
    return current_user.watchlist


@router.post("/{content_id}/watch-history")
async def update_watch_history(
    content_id: int,
    duration_watched: Optional[int] = None,
    is_completed: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update watch history"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Find or create watch history
    watch_history = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id,
        WatchHistory.content_id == content_id
    ).first()
    
    if not watch_history:
        watch_history = WatchHistory(
            user_id=current_user.id,
            content_id=content_id,
            duration_watched=duration_watched,
            is_completed=is_completed,
        )
    else:
        watch_history.duration_watched = duration_watched
        watch_history.is_completed = is_completed
    
    db.add(watch_history)
    db.commit()
    
    return {"message": "Watch history updated"}


@router.get("/user/continue-watching", response_model=List[ContentDetailResponse])
async def get_continue_watching(
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get continue watching list"""
    histories = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id,
        WatchHistory.is_completed == False
    ).order_by(WatchHistory.last_watched_at.desc()).limit(limit).all()
    
    # Extract unique contents
    contents = [h.content for h in histories]
    return contents


# ============================================
# Genres & Categories
# ============================================

@router.get("/genres", response_model=List)
async def list_genres(db: Session = Depends(get_db)):
    """Get all genres"""
    genres = db.query(Genre).all()
    return genres


@router.get("/categories", response_model=List)
async def list_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories
