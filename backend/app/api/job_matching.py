"""
Job Matching API Endpoints

Provides endpoints for job matching, recommendations, and matching analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, UserType
from ..models.job_matching import (
    JobMatchScore, JobRecommendation, CandidateJobInteraction,
    MatchingPreferences, InteractionType, NotificationFrequency
)
from ..services.job_matching_service import JobMatchingService, JobMatchingNotificationService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matching", tags=["job-matching"])


# Pydantic models for API
class MatchScoreResponse(BaseModel):
    job_id: str
    candidate_id: str
    overall_score: float
    skill_match_score: Optional[float]
    experience_match_score: Optional[float]
    location_match_score: Optional[float]
    salary_match_score: Optional[float]
    collaborative_score: Optional[float]
    content_based_score: Optional[float]
    confidence_level: Optional[float]
    match_reasons: List[str]
    improvement_suggestions: List[str]


class JobRecommendationResponse(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    location: Optional[str]
    remote_type: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    match_score: MatchScoreResponse
    recommended_at: datetime


class CandidateRecommendationResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    current_title: Optional[str]
    experience_years: int
    location: Optional[str]
    match_score: MatchScoreResponse


class MatchingPreferencesRequest(BaseModel):
    notification_frequency: NotificationFrequency = NotificationFrequency.WEEKLY
    min_match_score: float = Field(ge=0.0, le=1.0, default=0.6)
    preferred_job_types: Optional[List[str]] = None
    excluded_companies: Optional[List[str]] = None
    max_commute_distance: Optional[int] = None
    salary_importance_weight: float = Field(ge=0.0, le=1.0, default=0.3)
    location_importance_weight: float = Field(ge=0.0, le=1.0, default=0.2)
    skill_importance_weight: float = Field(ge=0.0, le=1.0, default=0.5)
    allow_overqualified_matches: bool = True
    allow_underqualified_matches: bool = False


class InteractionRequest(BaseModel):
    job_id: str
    interaction_type: InteractionType
    interaction_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/recommendations", response_model=List[JobRecommendationResponse])
async def get_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized job recommendations for the current candidate.
    """
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Only candidates can get job recommendations")
    
    try:
        matching_service = JobMatchingService(db)
        recommendations = matching_service.get_job_recommendations(
            candidate_id=str(current_user.id),
            limit=limit,
            min_score=min_score
        )
        
        response = []
        for rec in recommendations:
            job = rec.job_posting
            company_name = job.company.company_profile.company_name if job.company.company_profile else job.company.full_name
            
            response.append(JobRecommendationResponse(
                job_id=str(job.id),
                job_title=job.title,
                company_name=company_name,
                location=job.location,
                remote_type=job.remote_type,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                match_score=MatchScoreResponse(
                    job_id=rec.match_score.job_id,
                    candidate_id=rec.match_score.candidate_id,
                    overall_score=rec.match_score.overall_score,
                    skill_match_score=rec.match_score.skill_match_score,
                    experience_match_score=rec.match_score.experience_match_score,
                    location_match_score=rec.match_score.location_match_score,
                    salary_match_score=rec.match_score.salary_match_score,
                    collaborative_score=rec.match_score.collaborative_score,
                    content_based_score=rec.match_score.content_based_score,
                    confidence_level=rec.match_score.confidence_level,
                    match_reasons=rec.match_score.match_reasons,
                    improvement_suggestions=rec.match_score.improvement_suggestions
                ),
                recommended_at=rec.recommended_at
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting job recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get job recommendations")


@router.get("/candidates/{job_id}", response_model=List[CandidateRecommendationResponse])
async def get_candidate_recommendations(
    job_id: str,
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.6, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended candidates for a job posting.
    Only accessible by company users who own the job posting.
    """
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Only companies can get candidate recommendations")
    
    try:
        # Verify job ownership
        from ..models.job import JobPosting
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.company_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found or access denied")
        
        matching_service = JobMatchingService(db)
        recommendations = matching_service.get_candidate_recommendations(
            job_id=job_id,
            limit=limit,
            min_score=min_score
        )
        
        response = []
        for candidate, match_score in recommendations:
            response.append(CandidateRecommendationResponse(
                candidate_id=str(candidate.user_id),
                candidate_name=candidate.user.full_name,
                current_title=candidate.current_title,
                experience_years=candidate.experience_years,
                location=candidate.location,
                match_score=MatchScoreResponse(
                    job_id=match_score.job_id,
                    candidate_id=match_score.candidate_id,
                    overall_score=match_score.overall_score,
                    skill_match_score=match_score.skill_match_score,
                    experience_match_score=match_score.experience_match_score,
                    location_match_score=match_score.location_match_score,
                    salary_match_score=match_score.salary_match_score,
                    collaborative_score=match_score.collaborative_score,
                    content_based_score=match_score.content_based_score,
                    confidence_level=match_score.confidence_level,
                    match_reasons=match_score.match_reasons,
                    improvement_suggestions=match_score.improvement_suggestions
                )
            ))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get candidate recommendations")


@router.post("/interactions")
async def record_interaction(
    interaction: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a candidate's interaction with a job posting for collaborative filtering.
    """
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Only candidates can record interactions")
    
    try:
        # Verify job exists
        from ..models.job import JobPosting
        job = db.query(JobPosting).filter(JobPosting.id == interaction.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        # Create interaction record
        db_interaction = CandidateJobInteraction(
            candidate_id=current_user.id,
            job_posting_id=interaction.job_id,
            interaction_type=interaction.interaction_type,
            interaction_value=interaction.interaction_value,
            interaction_metadata=interaction.metadata
        )
        
        db.add(db_interaction)
        db.commit()
        
        return {"message": "Interaction recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.get("/preferences", response_model=MatchingPreferencesRequest)
async def get_matching_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's matching preferences.
    """
    try:
        preferences = db.query(MatchingPreferences).filter(
            MatchingPreferences.user_id == current_user.id
        ).first()
        
        if not preferences:
            # Return default preferences
            return MatchingPreferencesRequest()
        
        return MatchingPreferencesRequest(
            notification_frequency=preferences.notification_frequency,
            min_match_score=preferences.min_match_score,
            preferred_job_types=preferences.preferred_job_types,
            excluded_companies=[str(company_id) for company_id in preferences.excluded_companies] if preferences.excluded_companies else None,
            max_commute_distance=preferences.max_commute_distance,
            salary_importance_weight=preferences.salary_importance_weight,
            location_importance_weight=preferences.location_importance_weight,
            skill_importance_weight=preferences.skill_importance_weight,
            allow_overqualified_matches=preferences.allow_overqualified_matches,
            allow_underqualified_matches=preferences.allow_underqualified_matches
        )
        
    except Exception as e:
        logger.error(f"Error getting matching preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get matching preferences")


@router.put("/preferences")
async def update_matching_preferences(
    preferences: MatchingPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's matching preferences.
    """
    try:
        # Validate weights sum to approximately 1.0
        total_weight = (preferences.salary_importance_weight + 
                       preferences.location_importance_weight + 
                       preferences.skill_importance_weight)
        
        if abs(total_weight - 1.0) > 0.1:
            raise HTTPException(
                status_code=400, 
                detail="Importance weights should sum to approximately 1.0"
            )
        
        # Get or create preferences
        db_preferences = db.query(MatchingPreferences).filter(
            MatchingPreferences.user_id == current_user.id
        ).first()
        
        if not db_preferences:
            db_preferences = MatchingPreferences(user_id=current_user.id)
            db.add(db_preferences)
        
        # Update preferences
        db_preferences.notification_frequency = preferences.notification_frequency
        db_preferences.min_match_score = preferences.min_match_score
        db_preferences.preferred_job_types = preferences.preferred_job_types
        db_preferences.excluded_companies = [uuid.UUID(company_id) for company_id in preferences.excluded_companies] if preferences.excluded_companies else None
        db_preferences.max_commute_distance = preferences.max_commute_distance
        db_preferences.salary_importance_weight = preferences.salary_importance_weight
        db_preferences.location_importance_weight = preferences.location_importance_weight
        db_preferences.skill_importance_weight = preferences.skill_importance_weight
        db_preferences.allow_overqualified_matches = preferences.allow_overqualified_matches
        db_preferences.allow_underqualified_matches = preferences.allow_underqualified_matches
        
        db.commit()
        
        # Trigger background task to update match scores
        if current_user.user_type == UserType.CANDIDATE:
            matching_service = JobMatchingService(db)
            matching_service.update_match_scores_for_candidate(str(current_user.id))
        
        return {"message": "Matching preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating matching preferences: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update matching preferences")


@router.post("/notify-matches/{job_id}")
async def notify_job_matches(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send notifications to candidates about a new job posting that matches their profile.
    Only accessible by company users who own the job posting.
    """
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Only companies can send match notifications")
    
    try:
        # Verify job ownership
        from ..models.job import JobPosting
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.company_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found or access denied")
        
        # Add background task to send notifications
        def send_notifications():
            notification_service = JobMatchingNotificationService(db)
            notifications_sent = notification_service.notify_new_job_matches(job_id)
            logger.info(f"Sent {notifications_sent} job match notifications for job {job_id}")
        
        background_tasks.add_task(send_notifications)
        
        return {"message": "Job match notifications will be sent in the background"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating job match notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate job match notifications")


@router.get("/analytics/{job_id}")
async def get_job_matching_analytics(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get matching analytics for a job posting.
    Only accessible by company users who own the job posting.
    """
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Only companies can view matching analytics")
    
    try:
        # Verify job ownership
        from ..models.job import JobPosting
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.company_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found or access denied")
        
        matching_service = JobMatchingService(db)
        analytics = matching_service.get_match_analytics(job_id)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job matching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get matching analytics")


@router.post("/update-scores/{candidate_id}")
async def update_candidate_match_scores(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update match scores for a candidate after profile changes.
    Only accessible by the candidate themselves or admin users.
    """
    if current_user.user_type == UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Companies cannot update candidate match scores")
    
    if current_user.user_type == UserType.CANDIDATE and str(current_user.id) != candidate_id:
        raise HTTPException(status_code=403, detail="Can only update your own match scores")
    
    try:
        # Add background task to update match scores
        def update_scores():
            matching_service = JobMatchingService(db)
            matching_service.update_match_scores_for_candidate(candidate_id)
            
            # Send notifications about new high-quality matches
            notification_service = JobMatchingNotificationService(db)
            new_matches = notification_service.notify_skill_improvement_matches(candidate_id)
            logger.info(f"Found {new_matches} new high-quality matches for candidate {candidate_id}")
        
        background_tasks.add_task(update_scores)
        
        return {"message": "Match scores will be updated in the background"}
        
    except Exception as e:
        logger.error(f"Error initiating match score update: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate match score update")