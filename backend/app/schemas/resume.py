"""Resume Builder Schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ResumeContentSection(BaseModel):
    """Resume content section"""
    type: str  # summary, experience, education, skills, etc.
    content: Dict[str, Any]


class ResumeCreate(BaseModel):
    """Create resume"""
    title: str = Field(..., max_length=200)
    template_id: str = "professional"
    content: Dict[str, Any] = {}


class ResumeUpdate(BaseModel):
    """Update resume"""
    title: Optional[str] = Field(None, max_length=200)
    template_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    is_primary: Optional[bool] = None


class ResumeResponse(BaseModel):
    """Resume response"""
    id: int
    user_id: int
    title: str
    template_id: str
    content: Dict[str, Any]
    ats_score: Optional[float]
    keywords: List[str]
    is_primary: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeExportRequest(BaseModel):
    """Export resume"""
    format: str = Field(..., pattern="^(pdf|docx|txt)$")


class ResumeExportResponse(BaseModel):
    """Export response"""
    id: int
    resume_id: int
    format: str
    file_url: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class ATSOptimizationRequest(BaseModel):
    """ATS optimization request"""
    job_id: Optional[int] = None
    job_description: Optional[str] = None


class ATSOptimizationResponse(BaseModel):
    """ATS optimization response"""
    id: int
    resume_id: int
    job_id: Optional[int]
    score: float
    suggestions: List[Dict[str, Any]]
    missing_keywords: List[str]
    formatting_issues: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AIContentSuggestion(BaseModel):
    """AI content suggestion"""
    section: str
    original: str
    suggested: str
    reason: str
    impact: str  # high, medium, low
