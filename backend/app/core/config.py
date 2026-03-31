"""
Configuration management for the streaming platform
"""
import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Core
    APP_NAME: str = "StreamBox"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # JWT/Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 30
    
    # OAuth (Google)
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URL: str = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/api/auth/google/callback")
    
    # Security
    ENABLE_RECAPTCHA: bool = os.getenv("ENABLE_RECAPTCHA", "false").lower() == "true"
    RECAPTCHA_SECRET_KEY: Optional[str] = os.getenv("RECAPTCHA_SECRET_KEY")
    RECAPTCHA_VERSION: str = os.getenv("RECAPTCHA_VERSION", "v3")
    
    ENABLE_TURNSTILE: bool = os.getenv("ENABLE_TURNSTILE", "false").lower() == "true"
    TURNSTILE_SECRET_KEY: Optional[str] = os.getenv("TURNSTILE_SECRET_KEY")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_API: str = "100/minute"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    if os.getenv("CORS_ORIGINS"):
        CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")
    
    # TMDB
    TMDB_API_KEY: Optional[str] = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    
    # Storage
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local")  # local, s3, r2, b2
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Cloudflare R2
    CF_ACCOUNT_ID: Optional[str] = os.getenv("CF_ACCOUNT_ID")
    CF_ACCESS_KEY_ID: Optional[str] = os.getenv("CF_ACCESS_KEY_ID")
    CF_SECRET_ACCESS_KEY: Optional[str] = os.getenv("CF_SECRET_ACCESS_KEY")
    CF_BUCKET_NAME: Optional[str] = os.getenv("CF_BUCKET_NAME")
    
    # Backblaze B2
    B2_APPLICATION_KEY_ID: Optional[str] = os.getenv("B2_APPLICATION_KEY_ID")
    B2_APPLICATION_KEY: Optional[str] = os.getenv("B2_APPLICATION_KEY")
    B2_BUCKET_ID: Optional[str] = os.getenv("B2_BUCKET_ID")
    
    # Email/SMTP
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL", "noreply@streambox.app")
    
    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Admin
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@streambox.app")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")  # Change in production!
    
    # API
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
