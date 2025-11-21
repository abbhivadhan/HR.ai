"""Resume Builder API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.resume import Resume
from backend.app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ResumeResponse,
    ResumeExportRequest, ResumeExportResponse,
    ATSOptimizationRequest, ATSOptimizationResponse,
    AIContentSuggestion
)
from backend.app.services.resume_builder_service import ResumeBuilderService

router = APIRouter(prefix="/api/resume-builder", tags=["Resume Builder"])
resume_service = ResumeBuilderService()


@router.post("/resumes", response_model=ResumeResponse)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resume"""
    resume = await resume_service.create_resume(
        db=db,
        user_id=int(current_user.id),
        title=resume_data.title,
        template_id=resume_data.template_id,
        content=resume_data.content
    )
    return resume


@router.get("/resumes", response_model=List[ResumeResponse])
def get_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's resumes"""
    resumes = db.query(Resume).filter(
        Resume.user_id == int(current_user.id)
    ).order_by(Resume.updated_at.desc()).all()
    
    return resumes


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.put("/resumes/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    updates: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(resume, key, value)
    
    from datetime import datetime
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted"}


@router.get("/resumes/{resume_id}/suggestions", response_model=List[AIContentSuggestion])
async def get_ai_suggestions(
    resume_id: int,
    section: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI content suggestions"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    suggestions = await resume_service.get_ai_suggestions(
        db=db,
        resume_id=resume_id,
        section=section
    )
    
    return suggestions


@router.post("/resumes/{resume_id}/optimize", response_model=ATSOptimizationResponse)
async def optimize_for_ats(
    resume_id: int,
    request: ATSOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize resume for ATS"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    optimization = await resume_service.optimize_for_ats(
        db=db,
        resume_id=resume_id,
        job_id=request.job_id,
        job_description=request.job_description
    )
    
    return optimization


@router.post("/resumes/{resume_id}/export", response_model=ResumeExportResponse)
async def export_resume(
    resume_id: int,
    request: ResumeExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export resume to PDF/DOCX"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == int(current_user.id)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    export = await resume_service.export_resume(
        db=db,
        resume_id=resume_id,
        format=request.format
    )
    
    return export


@router.get("/templates")
def get_resume_templates():
    """Get available resume templates"""
    templates = [
        {
            "id": "professional",
            "name": "Professional",
            "description": "Clean and professional design",
            "preview_url": "/templates/professional.png"
        },
        {
            "id": "modern",
            "name": "Modern",
            "description": "Contemporary design with color accents",
            "preview_url": "/templates/modern.png"
        },
        {
            "id": "minimal",
            "name": "Minimal",
            "description": "Simple and elegant",
            "preview_url": "/templates/minimal.png"
        },
        {
            "id": "creative",
            "name": "Creative",
            "description": "Bold and creative design",
            "preview_url": "/templates/creative.png"
        }
    ]
    
    return templates
