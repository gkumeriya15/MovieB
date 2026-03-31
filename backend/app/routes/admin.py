"""
Admin routes - Dashboard and management APIs
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    User, Content, Genre, Category, Advertisement, 
    HomePage, SystemSetting, UserRole, Comment
)
from app.routes.auth import get_admin_user
from app.schemas import UserResponse, SystemSettingResponse, HomePageSectionResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# Admin Users Management
# ============================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset((page - 1) * limit).limit(limit).all()
    return users


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Change user role (admin only)"""
    if new_role not in ["admin", "moderator", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = UserRole(new_role)
    db.add(user)
    db.commit()
    
    return {"message": f"User role changed to {new_role}"}


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Toggle user active status (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.add(user)
    db.commit()
    
    return {"message": f"User is now {'active' if user.is_active else 'inactive'}"}


# ============================================
# Content Management
# ============================================

@router.post("/content")
async def create_content(
    title: str,
    content_type: str,
    description: Optional[str] = None,
    poster_url: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create new content (admin only)"""
    # Create slug from title
    slug = title.lower().replace(" ", "-").replace("'", "")
    
    content = Content(
        title=title,
        slug=slug,
        description=description,
        content_type=content_type,
        poster_url=poster_url,
    )
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.patch("/content/{content_id}")
async def update_content(
    content_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_active: Optional[bool] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Update content (admin only)"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if title:
        content.title = title
    if description is not None:
        content.description = description
    if is_featured is not None:
        content.is_featured = is_featured
    if is_active is not None:
        content.is_active = is_active
    
    content.updated_at = datetime.utcnow()
    db.add(content)
    db.commit()
    
    return {"message": "Content updated"}


@router.delete("/content/{content_id}")
async def delete_content(
    content_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Delete content (admin only)"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"message": "Content deleted"}


# ============================================
# Genre & Category Management
# ============================================

@router.post("/genres")
async def create_genre(
    name: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create genre (admin only)"""
    slug = name.lower().replace(" ", "-")
    
    genre = Genre(name=name, slug=slug)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    
    return genre


@router.post("/categories")
async def create_category(
    name: str,
    description: Optional[str] = None,
    icon_url: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create category (admin only)"""
    slug = name.lower().replace(" ", "-")
    
    category = Category(
        name=name,
        slug=slug,
        description=description,
        icon_url=icon_url,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


# ============================================
# Advertisement Management
# ============================================

@router.post("/ads")
async def create_ad(
    title: str,
    ad_type: str,
    placement: str,
    image_url: Optional[str] = None,
    target_url: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create advertisement (admin only)"""
    ad = Advertisement(
        title=title,
        ad_type=ad_type,
        placement=placement,
        image_url=image_url,
        target_url=target_url,
    )
    
    db.add(ad)
    db.commit()
    db.refresh(ad)
    
    return ad


@router.get("/ads")
async def list_ads(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all ads (admin only)"""
    ads = db.query(Advertisement).all()
    return ads


@router.patch("/ads/{ad_id}")
async def update_ad(
    ad_id: int,
    is_active: Optional[bool] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Update advertisement (admin only)"""
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    if is_active is not None:
        ad.is_active = is_active
    
    db.add(ad)
    db.commit()
    
    return {"message": "Ad updated"}


# ============================================
# System Settings
# ============================================

@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_settings(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get all system settings (admin only)"""
    settings = db.query(SystemSetting).all()
    return settings


@router.post("/settings")
async def create_setting(
    key: str,
    value: str,
    setting_type: str = "string",
    description: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create system setting (admin only)"""
    setting = SystemSetting(
        key=key,
        value=value,
        setting_type=setting_type,
        description=description,
    )
    
    db.add(setting)
    db.commit()
    db.refresh(setting)
    
    return setting


@router.patch("/settings/{setting_id}")
async def update_setting(
    setting_id: int,
    value: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Update system setting (admin only)"""
    setting = db.query(SystemSetting).filter(SystemSetting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    if value is not None:
        setting.value = value
    
    setting.updated_at = datetime.utcnow()
    db.add(setting)
    db.commit()
    
    return {"message": "Setting updated"}


# ============================================
# HomePage Sections Management
# ============================================

@router.get("/homepage-sections", response_model=List[HomePageSectionResponse])
async def get_homepage_sections(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get homepage sections (admin only)"""
    sections = db.query(HomePage).order_by(HomePage.order).all()
    return sections


@router.post("/homepage-sections")
async def create_homepage_section(
    section_name: str,
    title: str,
    section_type: str,
    order: int = 0,
    is_active: bool = True,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create homepage section (admin only)"""
    section = HomePage(
        section_name=section_name,
        title=title,
        section_type=section_type,
        order=order,
        is_active=is_active,
    )
    
    db.add(section)
    db.commit()
    db.refresh(section)
    
    return section


@router.patch("/homepage-sections/{section_id}")
async def update_homepage_section(
    section_id: int,
    title: Optional[str] = None,
    is_active: Optional[bool] = None,
    order: Optional[int] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Update homepage section (admin only)"""
    section = db.query(HomePage).filter(HomePage.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    if title:
        section.title = title
    if is_active is not None:
        section.is_active = is_active
    if order is not None:
        section.order = order
    
    section.updated_at = datetime.utcnow()
    db.add(section)
    db.commit()
    
    return {"message": "Section updated"}


# ============================================
# Comments Moderation
# ============================================

@router.get("/comments")
async def get_pending_comments(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get comments for moderation (admin only)"""
    comments = db.query(Comment).filter(Comment.is_approved == False).all()
    return comments


@router.patch("/comments/{comment_id}/approve")
async def approve_comment(
    comment_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Approve comment (admin only)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment.is_approved = True
    db.add(comment)
    db.commit()
    
    return {"message": "Comment approved"}


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Delete comment (admin only)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted"}


# ============================================
# Statistics & Analytics
# ============================================

@router.get("/stats")
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get platform statistics (admin only)"""
    total_users = db.query(User).count()
    total_content = db.query(Content).count()
    total_movies = db.query(Content).filter(Content.content_type == "movie").count()
    total_tv_shows = db.query(Content).filter(Content.content_type == "tv_show").count()
    total_anime = db.query(Content).filter(Content.content_type == "anime").count()
    
    return {
        "total_users": total_users,
        "total_content": total_content,
        "total_movies": total_movies,
        "total_tv_shows": total_tv_shows,
        "total_anime": total_anime,
    }
