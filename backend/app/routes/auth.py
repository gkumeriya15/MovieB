"""
Authentication routes
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models import User, UserRole
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserDetailResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(optional=True)


# ============================================
# Helper Functions
# ============================================

def get_current_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ============================================
# Public Routes
# ============================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_create.email) | (User.username == user_create.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    # TODO: Add reCAPTCHA validation if enabled
    # if settings.ENABLE_RECAPTCHA:
    #     captcha_token = request.headers.get("x-captcha-token")
    #     if not captcha_token or not verify_recaptcha(captcha_token):
    #         raise HTTPException(status_code=400, detail="CAPTCHA verification failed")

    # Create new user
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        password_hash=hash_password(user_create.password),
        full_name=user_create.full_name,
        role=UserRole.USER,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"New user registered: {db_user.email}")
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Login user and get tokens"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email,
    )

    logger.info(f"User logged in: {user.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token"""
    token_data = verify_token(request.refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Get user
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
    )
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
    )


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard tokens)"""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


# ============================================
# OAuth Routes
# ============================================

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback"""
    # TODO: Implement Google OAuth token exchange
    # 1. Exchange code for tokens
    # 2. Get user info from Google
    # 3. Create or update user in DB
    # 4. Return JWT tokens
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ============================================
# User Management Routes
# ============================================

@router.put("/profile", response_model=UserDetailResponse)
async def update_profile(
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile"""
    if full_name is not None:
        current_user.full_name = full_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    
    current_user.updated_at = datetime.utcnow()
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    if not verify_password(old_password, current_user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password",
        )

    current_user.password_hash = hash_password(new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.add(current_user)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}
