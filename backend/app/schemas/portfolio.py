"""Portfolio and Video Resume Schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class PortfolioCreate(BaseModel):
    """Create portfolio"""
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    template_id: str = "modern"
    is_public: bool = True


class PortfolioUpdate(BaseModel):
    """Update portfolio"""
    video_intro_url: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    template_id: Optional[str] = None
    is_public: Optional[bool] = None


class PortfolioResponse(BaseModel):
    """Portfolio response"""
    id: int
    user_id: int
    video_intro_url: Optional[str]
    video_duration: Optional[int]
    headline: Optional[str]
    bio: Optional[str]
    template_id: str
    is_public: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioProjectCreate(BaseModel):
    """Create portfolio project"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    technologies: List[str] = []
    media_urls: List[str] = []
    code_snippets: List[Dict[str, str]] = []
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    display_order: int = 0


class PortfolioProjectUpdate(BaseModel):
    """Update portfolio project"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    code_snippets: Optional[List[Dict[str, str]]] = None
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    display_order: Optional[int] = None


class PortfolioProjectResponse(BaseModel):
    """Portfolio project response"""
    id: int
    portfolio_id: int
    title: str
    description: Optional[str]
    technologies: List[str]
    media_urls: List[str]
    code_snippets: List[Dict[str, str]]
    live_url: Optional[str]
    github_url: Optional[str]
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class AchievementCreate(BaseModel):
    """Create achievement"""
    badge_type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    issuer: Optional[str] = Field(None, max_length=200)
    date_earned: Optional[datetime] = None
    verification_url: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)


class AchievementResponse(BaseModel):
    """Achievement response"""
    id: int
    portfolio_id: int
    badge_type: str
    title: str
    description: Optional[str]
    issuer: Optional[str]
    date_earned: Optional[datetime]
    verification_url: Optional[str]
    icon: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class VideoUploadRequest(BaseModel):
    """Video upload request"""
    file_name: str
    file_size: int
    content_type: str = "video/mp4"


class VideoUploadResponse(BaseModel):
    """Video upload response"""
    upload_url: str
    video_url: str
    expires_in: int
