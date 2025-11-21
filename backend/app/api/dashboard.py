from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, UserType
from ..models.profile import CandidateProfile, CompanyProfile
from ..models.job import JobPosting, JobApplication, ApplicationStatus, JobStatus
from ..models.assessment import Assessment, AssessmentStatus
from ..models.interview import Interview, InterviewStatus
from ..schemas.dashboard import (
    CandidateStatsResponse,
    CompanyAnalyticsResponse,
    AdminMetricsResponse,
    NotificationResponse,
    ChartDataResponse,
    CandidateRecommendationResponse,
    JobPostingStatsResponse,
    ApplicationStatsResponse
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Candidate Dashboard Endpoints
@router.get("/candidate/stats", response_model=CandidateStatsResponse)
async def get_candidate_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate dashboard statistics"""
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get total applications
    total_applications = db.query(JobApplication).filter(
        JobApplication.candidate_id == current_user.id
    ).count()
    
    # Get matching jobs (simplified - would use ML matching in production)
    matching_jobs = db.query(JobPosting).filter(
        JobPosting.status == JobStatus.ACTIVE
    ).count()
    
    # Get profile views (mock data - would track actual views)
    profile_views = 45  # Mock data
    
    # Get completed assessments
    assessments_completed = db.query(Assessment).filter(
        and_(
            Assessment.candidate_id == current_user.id,
            Assessment.status == AssessmentStatus.COMPLETED
        )
    ).count()
    
    # Get average assessment score
    avg_score_result = db.query(func.avg(Assessment.percentage_score)).filter(
        and_(
            Assessment.candidate_id == current_user.id,
            Assessment.status == AssessmentStatus.COMPLETED,
            Assessment.percentage_score.isnot(None)
        )
    ).scalar()
    
    average_score = round(avg_score_result, 1) if avg_score_result else 0
    
    # Get scheduled interviews
    interviews_scheduled = db.query(Interview).filter(
        and_(
            Interview.candidate_id == current_user.id,
            Interview.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.IN_PROGRESS])
        )
    ).count()
    
    return CandidateStatsResponse(
        total_applications=total_applications,
        matching_jobs=matching_jobs,
        profile_views=profile_views,
        assessments_completed=assessments_completed,
        average_score=average_score,
        interviews_scheduled=interviews_scheduled
    )


@router.get("/candidate/recommendations", response_model=List[CandidateRecommendationResponse])
async def get_candidate_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job recommendations for candidate"""
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get candidate profile
    candidate_profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    # Get active job postings (simplified matching)
    jobs = db.query(JobPosting).join(User).filter(
        JobPosting.status == JobStatus.ACTIVE
    ).order_by(desc(JobPosting.posted_at)).limit(limit).all()
    
    recommendations = []
    for job in jobs:
        company = job.company
        company_profile = db.query(CompanyProfile).filter(
            CompanyProfile.user_id == company.id
        ).first()
        
        # Mock match score calculation (would use ML in production)
        match_score = 85 + (hash(job.id) % 15)  # Mock score between 85-99
        
        recommendations.append(CandidateRecommendationResponse(
            id=str(job.id),
            job_title=job.title,
            company_name=company_profile.company_name if company_profile else company.full_name,
            match_score=match_score,
            location=job.location or "Remote",
            salary_range=f"${job.salary_min//1000}k - ${job.salary_max//1000}k" if job.salary_min and job.salary_max else "Competitive",
            posted_date=job.posted_at or job.created_at,
            skills=[]  # Would extract from job requirements
        ))
    
    return recommendations


@router.get("/candidate/skill-scores", response_model=ChartDataResponse)
async def get_candidate_skill_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate skill assessment scores"""
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get skill scores from assessments
    assessments = db.query(Assessment).filter(
        and_(
            Assessment.candidate_id == current_user.id,
            Assessment.status == AssessmentStatus.COMPLETED,
            Assessment.skill_scores.isnot(None)
        )
    ).all()
    
    # Aggregate skill scores
    skill_totals = {}
    skill_counts = {}
    
    for assessment in assessments:
        if assessment.skill_scores:
            scores = json.loads(assessment.skill_scores) if isinstance(assessment.skill_scores, str) else assessment.skill_scores
            for skill, score in scores.items():
                if skill not in skill_totals:
                    skill_totals[skill] = 0
                    skill_counts[skill] = 0
                skill_totals[skill] += score
                skill_counts[skill] += 1
    
    # Calculate averages
    labels = []
    data = []
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    
    for i, (skill, total) in enumerate(skill_totals.items()):
        labels.append(skill)
        data.append(round(total / skill_counts[skill], 1))
    
    return ChartDataResponse(
        labels=labels,
        datasets=[{
            "label": "Skill Scores",
            "data": data,
            "backgroundColor": colors[:len(data)]
        }]
    )


@router.get("/candidate/application-trends", response_model=ChartDataResponse)
async def get_candidate_application_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate application trends over time"""
    if current_user.user_type != UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get applications from last 6 months
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    applications = db.query(
        func.date_trunc('month', JobApplication.applied_at).label('month'),
        func.count(JobApplication.id).label('count')
    ).filter(
        and_(
            JobApplication.candidate_id == current_user.id,
            JobApplication.applied_at >= six_months_ago
        )
    ).group_by(
        func.date_trunc('month', JobApplication.applied_at)
    ).order_by('month').all()
    
    # Generate labels and data
    labels = []
    data = []
    
    for app in applications:
        labels.append(app.month.strftime('%b'))
        data.append(app.count)
    
    return ChartDataResponse(
        labels=labels,
        datasets=[{
            "label": "Applications",
            "data": data,
            "backgroundColor": "#3B82F6",
            "borderColor": "#3B82F6"
        }]
    )


# Company Dashboard Endpoints
@router.get("/company/analytics", response_model=CompanyAnalyticsResponse)
async def get_company_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company dashboard analytics"""
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Job postings stats
    job_stats = db.query(
        func.count(JobPosting.id).label('total'),
        func.sum(func.case([(JobPosting.status == JobStatus.ACTIVE, 1)], else_=0)).label('active'),
        func.sum(func.case([(JobPosting.status == JobStatus.FILLED, 1)], else_=0)).label('filled'),
        func.sum(func.case([(JobPosting.status == JobStatus.EXPIRED, 1)], else_=0)).label('expired')
    ).filter(JobPosting.company_id == current_user.id).first()
    
    # Applications stats
    app_stats = db.query(
        func.count(JobApplication.id).label('total'),
        func.sum(func.case([(JobApplication.status == ApplicationStatus.PENDING, 1)], else_=0)).label('pending'),
        func.sum(func.case([(JobApplication.status == ApplicationStatus.REVIEWING, 1)], else_=0)).label('reviewed'),
        func.sum(func.case([(JobApplication.status == ApplicationStatus.SHORTLISTED, 1)], else_=0)).label('shortlisted'),
        func.sum(func.case([(JobApplication.status == ApplicationStatus.ACCEPTED, 1)], else_=0)).label('hired')
    ).join(JobPosting).filter(JobPosting.company_id == current_user.id).first()
    
    # Performance metrics (mock data)
    avg_time_to_hire = 18
    application_rate = 15.6
    interview_to_hire_ratio = 0.38
    
    return CompanyAnalyticsResponse(
        job_postings={
            "total": job_stats.total or 0,
            "active": job_stats.active or 0,
            "filled": job_stats.filled or 0,
            "expired": job_stats.expired or 0
        },
        applications={
            "total": app_stats.total or 0,
            "pending": app_stats.pending or 0,
            "reviewed": app_stats.reviewed or 0,
            "shortlisted": app_stats.shortlisted or 0,
            "hired": app_stats.hired or 0
        },
        candidates={
            "total_viewed": 1250,  # Mock data
            "average_score": 78.5,
            "top_skills": ["JavaScript", "React", "Python", "Node.js", "AWS"]
        },
        performance={
            "average_time_to_hire": avg_time_to_hire,
            "application_rate": application_rate,
            "interview_to_hire_ratio": interview_to_hire_ratio
        }
    )


@router.get("/company/job-postings", response_model=List[JobPostingStatsResponse])
async def get_company_job_postings(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company job postings with stats"""
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Access denied")
    
    jobs = db.query(JobPosting).filter(
        JobPosting.company_id == current_user.id
    ).order_by(desc(JobPosting.created_at)).limit(limit).all()
    
    job_stats = []
    for job in jobs:
        applications_count = db.query(JobApplication).filter(
            JobApplication.job_posting_id == job.id
        ).count()
        
        job_stats.append(JobPostingStatsResponse(
            id=str(job.id),
            title=job.title,
            status=job.status,
            applications=applications_count,
            views=job.view_count,
            posted_date=job.posted_at or job.created_at,
            location=job.location or "Remote"
        ))
    
    return job_stats


@router.get("/company/applications", response_model=List[ApplicationStatsResponse])
async def get_company_applications(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent applications for company jobs"""
    if current_user.user_type != UserType.COMPANY:
        raise HTTPException(status_code=403, detail="Access denied")
    
    applications = db.query(JobApplication).join(JobPosting).join(User).filter(
        JobPosting.company_id == current_user.id
    ).order_by(desc(JobApplication.applied_at)).limit(limit).all()
    
    app_stats = []
    for app in applications:
        candidate = app.candidate
        
        # Mock match score (would use ML in production)
        match_score = 85 + (hash(app.id) % 15)
        
        app_stats.append(ApplicationStatsResponse(
            id=str(app.id),
            candidate_name=candidate.full_name,
            job_title=app.job_posting.title,
            status=app.status,
            match_score=match_score,
            applied_date=app.applied_at
        ))
    
    return app_stats


# Admin Dashboard Endpoints
@router.get("/admin/metrics", response_model=AdminMetricsResponse)
async def get_admin_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard metrics"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # User stats
    total_users = db.query(User).count()
    candidates = db.query(User).filter(User.user_type == UserType.CANDIDATE).count()
    companies = db.query(User).filter(User.user_type == UserType.COMPANY).count()
    
    # Active users today (mock data)
    active_today = 1250
    new_this_week = 340
    
    # Platform stats
    total_jobs = db.query(JobPosting).count()
    total_applications = db.query(JobApplication).count()
    total_assessments = db.query(Assessment).count()
    total_interviews = db.query(Interview).count()
    
    # Engagement metrics (mock data)
    daily_active_users = 2340
    avg_session_time = 24.5
    bounce_rate = 12.8
    
    # Revenue metrics (mock data)
    monthly_recurring = 125000
    total_revenue = 890000
    churn_rate = 3.2
    
    return AdminMetricsResponse(
        users={
            "total": total_users,
            "candidates": candidates,
            "companies": companies,
            "active_today": active_today,
            "new_this_week": new_this_week
        },
        platform={
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "total_assessments": total_assessments,
            "total_interviews": total_interviews
        },
        engagement={
            "daily_active_users": daily_active_users,
            "average_session_time": avg_session_time,
            "bounce_rate": bounce_rate
        },
        revenue={
            "monthly_recurring": monthly_recurring,
            "total_revenue": total_revenue,
            "churn_rate": churn_rate
        }
    )


# Notifications endpoint
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    # Mock notifications - in production, you'd have a notifications table
    notifications = [
        {
            "id": "1",
            "type": "success",
            "title": "Assessment Completed",
            "message": "You scored 92% on the JavaScript assessment!",
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "read": False,
            "action_url": "/assessments/results/1"
        },
        {
            "id": "2",
            "type": "info",
            "title": "New Job Match",
            "message": "We found 3 new jobs that match your profile.",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "read": False,
            "action_url": "/jobs/recommendations"
        }
    ]
    
    return [NotificationResponse(**notif) for notif in notifications[:limit]]


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    # In production, update notification in database
    return {"message": "Notification marked as read"}


@router.patch("/notifications/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    # In production, update all user notifications in database
    return {"message": "All notifications marked as read"}


@router.delete("/notifications/{notification_id}")
async def dismiss_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss notification"""
    # In production, delete notification from database
    return {"message": "Notification dismissed"}