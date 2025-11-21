"""
REST API endpoints for interview management
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database import get_db
from ..models.interview import (
    Interview, InterviewSession, InterviewAnalysis, InterviewQuestion,
    InterviewType, InterviewStatus, SessionStatus
)
from ..models.job import JobApplication
from ..models.user import User
from ..services.webrtc_signaling import webrtc_signaling
from ..services.interview_question_service import interview_question_service
from ..auth.dependencies import get_current_user
from pydantic import BaseModel, Field
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interviews", tags=["interviews"])


# Pydantic models for request/response
class InterviewCreate(BaseModel):
    job_application_id: UUID
    interview_type: str = Field(..., regex="^(ai_screening|ai_technical|ai_behavioral|human_final)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=180)
    timezone: str = "UTC"
    ai_interviewer_persona: Optional[str] = None
    difficulty_level: str = Field(default="intermediate", regex="^(beginner|intermediate|advanced|expert)$")
    focus_areas: List[str] = Field(default_factory=list, max_items=10)
    max_questions: int = Field(default=10, ge=1, le=50)
    allow_retakes: bool = False
    recording_enabled: bool = True


class InterviewUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=180)
    status: Optional[str] = Field(None, regex="^(scheduled|in_progress|completed|cancelled|no_show|technical_issues)$")
    ai_interviewer_persona: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced|expert)$")
    focus_areas: Optional[List[str]] = Field(None, max_items=10)
    max_questions: Optional[int] = Field(None, ge=1, le=50)
    allow_retakes: Optional[bool] = None
    recording_enabled: Optional[bool] = None


class InterviewResponse(BaseModel):
    id: UUID
    job_application_id: UUID
    candidate_id: UUID
    company_id: UUID
    interview_type: str
    title: str
    description: Optional[str]
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    ai_interviewer_persona: Optional[str]
    difficulty_level: str
    focus_areas: List[str]
    max_questions: int
    allow_retakes: bool
    recording_enabled: bool
    overall_score: Optional[float]
    recommendation: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: UUID
    interview_id: UUID
    session_token: str
    room_id: str
    status: str
    joined_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    connection_quality: Optional[float]
    audio_quality: Optional[float]
    video_quality: Optional[float]
    latency_ms: Optional[int]
    recording_url: Optional[str]
    recording_duration: Optional[int]
    error_count: int
    reconnection_attempts: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionGenerationRequest(BaseModel):
    regenerate: bool = False
    focus_areas: Optional[List[str]] = None
    difficulty_override: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced|expert)$")
    question_count_override: Optional[int] = Field(None, ge=1, le=50)


class InterviewQuestionResponse(BaseModel):
    id: UUID
    interview_id: UUID
    question_text: str
    category: str
    difficulty_level: str
    expected_duration: int
    question_order: int
    is_follow_up: bool
    parent_question_id: Optional[UUID]
    skill_focus: List[str]
    context_data: Dict[str, Any]
    ai_generated: bool
    asked_at: Optional[datetime]
    answered_at: Optional[datetime]
    candidate_response: Optional[str]
    response_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class FollowUpRequest(BaseModel):
    parent_question_id: UUID
    candidate_response: str


@router.post("/", response_model=InterviewResponse)
async def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new interview"""
    try:
        # Verify job application exists and user has permission
        job_application = db.query(JobApplication).filter(
            JobApplication.id == interview_data.job_application_id
        ).first()
        
        if not job_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Check permissions (company can schedule interviews for their job postings)
        if (current_user.user_type == "company" and 
            job_application.job_posting.company_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to schedule interview for this application"
            )
        
        # Create interview
        interview = Interview(
            job_application_id=interview_data.job_application_id,
            candidate_id=job_application.candidate_id,
            company_id=job_application.job_posting.company_id,
            interview_type=interview_data.interview_type,
            title=interview_data.title,
            description=interview_data.description,
            scheduled_at=interview_data.scheduled_at,
            duration_minutes=interview_data.duration_minutes,
            timezone=interview_data.timezone,
            status=InterviewStatus.SCHEDULED,
            ai_interviewer_persona=interview_data.ai_interviewer_persona,
            difficulty_level=interview_data.difficulty_level,
            focus_areas=interview_data.focus_areas,
            max_questions=interview_data.max_questions,
            allow_retakes=interview_data.allow_retakes,
            recording_enabled=interview_data.recording_enabled
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        logger.info(f"Created interview {interview.id} for application {interview_data.job_application_id}")
        return interview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating interview: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview"
        )


@router.get("/", response_model=List[InterviewResponse])
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, regex="^(scheduled|in_progress|completed|cancelled|no_show|technical_issues)$"),
    interview_type: Optional[str] = Query(None, regex="^(ai_screening|ai_technical|ai_behavioral|human_final)$"),
    candidate_id: Optional[UUID] = None,
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List interviews with filtering"""
    try:
        query = db.query(Interview)
        
        # Apply user-based filtering
        if current_user.user_type == "candidate":
            query = query.filter(Interview.candidate_id == current_user.id)
        elif current_user.user_type == "company":
            query = query.filter(Interview.company_id == current_user.id)
        # Admin can see all interviews
        
        # Apply filters
        if status_filter:
            query = query.filter(Interview.status == status_filter)
        
        if interview_type:
            query = query.filter(Interview.interview_type == interview_type)
        
        if candidate_id:
            query = query.filter(Interview.candidate_id == candidate_id)
        
        if company_id:
            query = query.filter(Interview.company_id == company_id)
        
        # Order by scheduled date
        query = query.order_by(Interview.scheduled_at.desc())
        
        interviews = query.offset(skip).limit(limit).all()
        return interviews
        
    except Exception as e:
        logger.error(f"Error listing interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interviews"
        )


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions
        if (current_user.user_type == "candidate" and interview.candidate_id != current_user.id) or \
           (current_user.user_type == "company" and interview.company_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this interview"
            )
        
        return interview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview {interview_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview"
        )


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: UUID,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions (only company can update their interviews)
        if current_user.user_type != "company" or interview.company_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this interview"
            )
        
        # Update fields
        update_data = interview_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interview, field, value)
        
        interview.updated_at = datetime.now()
        db.commit()
        db.refresh(interview)
        
        logger.info(f"Updated interview {interview_id}")
        return interview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview {interview_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interview"
        )


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete/cancel an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions
        if current_user.user_type != "company" or interview.company_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this interview"
            )
        
        # Don't actually delete, just mark as cancelled
        interview.status = InterviewStatus.CANCELLED
        interview.updated_at = datetime.now()
        db.commit()
        
        logger.info(f"Cancelled interview {interview_id}")
        return {"message": "Interview cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interview {interview_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel interview"
        )


@router.post("/{interview_id}/session", response_model=SessionResponse)
async def create_interview_session(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a WebRTC session for an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions
        if (current_user.user_type == "candidate" and interview.candidate_id != current_user.id) or \
           (current_user.user_type == "company" and interview.company_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create session for this interview"
            )
        
        # Check if interview is scheduled
        if interview.status != InterviewStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create session for interview with status: {interview.status}"
            )
        
        # Create WebRTC session
        session = await webrtc_signaling.create_session(db, str(interview_id))
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create interview session"
            )
        
        logger.info(f"Created session {session.id} for interview {interview_id}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session for interview {interview_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview session"
        )


@router.get("/{interview_id}/sessions", response_model=List[SessionResponse])
async def get_interview_sessions(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sessions for an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions
        if (current_user.user_type == "candidate" and interview.candidate_id != current_user.id) or \
           (current_user.user_type == "company" and interview.company_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view sessions for this interview"
            )
        
        sessions = db.query(InterviewSession).filter(
            InterviewSession.interview_id == interview_id
        ).order_by(InterviewSession.created_at.desc()).all()
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sessions for interview {interview_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview sessions"
        )


@router.post("/session/{session_token}/join")
async def join_interview_session(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join an interview session"""
    try:
        # Determine user type for the session
        user_type = "candidate" if current_user.user_type == "candidate" else "ai_interviewer"
        
        # Join the session
        session_info = await webrtc_signaling.join_session(
            db, session_token, str(current_user.id), user_type
        )
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to join session"
            )
        
        logger.info(f"User {current_user.id} joined session with token {session_token}")
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining session {session_token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join interview session"
        )


@router.post("/{interview_id}/questions/generate", response_model=List[InterviewQuestionResponse])
async def generate_interview_questions(
    interview_id: UUID,
    request: QuestionGenerationRequest = QuestionGenerationRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered questions for an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions (company can generate questions for their interviews)
        if current_user.user_type != "company" or interview.company_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to generate questions for this interview"
            )
        
        # Check if questions already exist and regeneration is not requested
        existing_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).count()
        
        if existing_questions > 0 and not request.regenerate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questions already exist for this interview. Use regenerate=true to create new ones."
            )
        
        # Delete existing questions if regenerating
        if request.regenerate and existing_questions > 0:
            db.query(InterviewQuestion).filter(
                InterviewQuestion.interview_id == interview_id
            ).delete()
            db.commit()
        
        # Apply overrides if provided
        if request.focus_areas:
            interview.focus_areas = request.focus_areas
        if request.difficulty_override:
            interview.difficulty_level = request.difficulty_override
        if request.question_count_override:
            interview.max_questions = request.question_count_override
        
        # Generate questions
        questions_data = await interview_question_service.generate_interview_questions(
            db, str(interview_id)
        )
        
        # Retrieve stored questions from database
        stored_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).order_by(InterviewQuestion.question_order).all()
        
        logger.info(f"Generated {len(stored_questions)} questions for interview {interview_id}")
        return stored_questions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions for interview {interview_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate interview questions"
        )


@router.get("/{interview_id}/questions", response_model=List[InterviewQuestionResponse])
async def get_interview_questions(
    interview_id: UUID,
    include_responses: bool = Query(False, description="Include candidate responses"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for an interview"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions
        if (current_user.user_type == "candidate" and interview.candidate_id != current_user.id) or \
           (current_user.user_type == "company" and interview.company_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view questions for this interview"
            )
        
        # Get questions
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).order_by(InterviewQuestion.question_order).all()
        
        # Filter out responses if not requested or if candidate is viewing
        if not include_responses or current_user.user_type == "candidate":
            for question in questions:
                if hasattr(question, 'candidate_response'):
                    question.candidate_response = None
                if hasattr(question, 'response_score'):
                    question.response_score = None
        
        return questions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting questions for interview {interview_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview questions"
        )


@router.post("/{interview_id}/questions/follow-up", response_model=InterviewQuestionResponse)
async def generate_follow_up_question(
    interview_id: UUID,
    request: FollowUpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a follow-up question based on candidate response"""
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check permissions (company can generate follow-ups during interviews)
        if current_user.user_type != "company" or interview.company_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to generate follow-up questions"
            )
        
        # Verify parent question exists
        parent_question = db.query(InterviewQuestion).filter(
            and_(
                InterviewQuestion.id == request.parent_question_id,
                InterviewQuestion.interview_id == interview_id
            )
        ).first()
        
        if not parent_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent question not found"
            )
        
        # Generate follow-up question
        follow_up_data = await interview_question_service.generate_follow_up_question(
            db, str(request.parent_question_id), request.candidate_response, {}
        )
        
        if not follow_up_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate follow-up question"
            )
        
        # Get next question order
        max_order = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).count()
        
        # Create and store follow-up question
        follow_up_question = InterviewQuestion(
            interview_id=interview_id,
            question_text=follow_up_data["question_text"],
            category=follow_up_data["category"],
            difficulty_level=follow_up_data["difficulty_level"],
            expected_duration=follow_up_data["expected_duration"],
            question_order=max_order + 1,
            is_follow_up=True,
            parent_question_id=request.parent_question_id,
            generated_from_job_requirements=follow_up_data.get("ai_generated", True),
            skill_focus=follow_up_data.get("skill_focus", []),
            context_data=follow_up_data.get("context_data", {})
        )
        
        db.add(follow_up_question)
        db.commit()
        db.refresh(follow_up_question)
        
        logger.info(f"Generated follow-up question {follow_up_question.id} for interview {interview_id}")
        return follow_up_question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating follow-up question: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate follow-up question"
        )


@router.put("/questions/{question_id}/response")
async def submit_question_response(
    question_id: UUID,
    response_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit candidate response to a question"""
    try:
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Get interview to check permissions
        interview = db.query(Interview).filter(Interview.id == question.interview_id).first()
        
        # Check permissions (candidate can submit responses to their interview questions)
        if current_user.user_type != "candidate" or interview.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to submit response to this question"
            )
        
        # Update question with response
        question.candidate_response = response_data.get("response", "")
        question.response_duration = response_data.get("duration", 0)
        question.response_timestamp = datetime.now()
        question.answered_at = datetime.now()
        
        # Store audio/video analysis if provided
        if "audio_analysis" in response_data:
            question.audio_analysis = response_data["audio_analysis"]
        if "video_analysis" in response_data:
            question.video_analysis = response_data["video_analysis"]
        
        db.commit()
        
        logger.info(f"Submitted response for question {question_id}")
        return {"message": "Response submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response for question {question_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit question response"
        )

# AI 
Interview Analysis Models
class ResponseAnalysisRequest(BaseModel):
    transcript: str
    question: str
    duration: int
    question_type: str = "general"


class FullInterviewAnalysisRequest(BaseModel):
    interview_id: UUID
    responses: List[Dict[str, Any]]


# AI Interview Analysis Endpoints
@router.post("/ai-video/analyze-response")
async def analyze_response(
    request: ResponseAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a single interview response
    """
    try:
        from ..services.ai_interview_service import ai_interview_service
        
        analysis = ai_interview_service.analyze_response(
            transcript=request.transcript,
            question=request.question,
            duration=request.duration,
            question_type=request.question_type
        )
        
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze response: {str(e)}"
        )


@router.post("/ai-video/analyze-full-interview")
async def analyze_full_interview(
    request: FullInterviewAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze complete AI video interview
    """
    try:
        from ..services.ai_interview_service import ai_interview_service
        
        # Verify interview exists and belongs to user
        interview = db.query(Interview).filter(
            Interview.id == request.interview_id,
            Interview.candidate_id == current_user.id
        ).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Analyze full interview
        analysis = ai_interview_service.analyze_full_interview(request.responses)
        
        # Save analysis to database
        interview_analysis = InterviewAnalysis(
            interview_id=request.interview_id,
            overall_score=analysis['overall_score'],
            analysis_data=analysis,
            analyzed_at=datetime.utcnow()
        )
        db.add(interview_analysis)
        
        # Update interview status
        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(interview_analysis)
        
        return {
            "success": True,
            "analysis": analysis,
            "analysis_id": str(interview_analysis.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing full interview: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze interview: {str(e)}"
        )


@router.get("/ai-video/{interview_id}/analysis")
async def get_interview_analysis(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved interview analysis
    """
    try:
        # Verify interview exists and belongs to user
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.candidate_id == current_user.id
        ).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Get analysis
        analysis = db.query(InterviewAnalysis).filter(
            InterviewAnalysis.interview_id == interview_id
        ).order_by(InterviewAnalysis.analyzed_at.desc()).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return {
            "success": True,
            "analysis": analysis.analysis_data,
            "analyzed_at": analysis.analyzed_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )
