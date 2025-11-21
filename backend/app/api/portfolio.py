"""Portfolio API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.portfolio import Portfolio, PortfolioProject, Achievement
from backend.app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioResponse,
    PortfolioProjectCreate, PortfolioProjectUpdate, PortfolioProjectResponse,
    AchievementCreate, AchievementResponse,
    VideoUploadRequest, VideoUploadResponse
)
from backend.app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])
portfolio_service = PortfolioService()


@router.get("/me", response_model=PortfolioResponse)
def get_my_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's portfolio"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    return portfolio


@router.put("/me", response_model=PortfolioResponse)
def update_my_portfolio(
    updates: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's portfolio"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    updated_portfolio = portfolio_service.update_portfolio(
        db=db,
        portfolio_id=portfolio.id,
        updates=updates.dict(exclude_unset=True)
    )
    
    return updated_portfolio


@router.get("/{user_id}", response_model=PortfolioResponse)
def get_user_portfolio(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get public portfolio by user ID"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_public == True
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Increment view count
    portfolio_service.increment_view_count(db=db, portfolio_id=portfolio.id)
    
    return portfolio


@router.post("/video-upload", response_model=VideoUploadResponse)
def get_video_upload_url(
    request: VideoUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """Get presigned URL for video upload"""
    upload_data = portfolio_service.generate_video_upload_url(
        user_id=int(current_user.id),
        file_name=request.file_name,
        content_type=request.content_type
    )
    
    return upload_data


@router.post("/projects", response_model=PortfolioProjectResponse)
def add_project(
    project_data: PortfolioProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add project to portfolio"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    project = portfolio_service.add_project(
        db=db,
        portfolio_id=portfolio.id,
        project_data=project_data.dict()
    )
    
    return project


@router.get("/projects", response_model=List[PortfolioProjectResponse])
def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's projects"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    projects = db.query(PortfolioProject).filter(
        PortfolioProject.portfolio_id == portfolio.id
    ).order_by(PortfolioProject.display_order).all()
    
    return projects


@router.put("/projects/{project_id}", response_model=PortfolioProjectResponse)
def update_project(
    project_id: int,
    updates: PortfolioProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    project = db.query(PortfolioProject).filter(
        PortfolioProject.id == project_id,
        PortfolioProject.portfolio_id == portfolio.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    project = db.query(PortfolioProject).filter(
        PortfolioProject.id == project_id,
        PortfolioProject.portfolio_id == portfolio.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted"}


@router.post("/achievements", response_model=AchievementResponse)
def add_achievement(
    achievement_data: AchievementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add achievement/badge"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    achievement = portfolio_service.add_achievement(
        db=db,
        portfolio_id=portfolio.id,
        achievement_data=achievement_data.dict()
    )
    
    return achievement


@router.get("/achievements", response_model=List[AchievementResponse])
def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's achievements"""
    portfolio = portfolio_service.get_or_create_portfolio(
        db=db,
        user_id=int(current_user.id)
    )
    
    achievements = db.query(Achievement).filter(
        Achievement.portfolio_id == portfolio.id
    ).all()
    
    return achievements
