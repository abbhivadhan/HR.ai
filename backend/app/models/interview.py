from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class InterviewType(str, Enum):
    AI_SCREENING = "ai_screening"
    AI_TECHNICAL = "ai_technical"
    AI_BEHAVIORAL = "ai_behavioral"
    HUMAN_FINAL = "human_final"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    TECHNICAL_ISSUES = "technical_issues"


class SessionStatus(str, Enum):
    WAITING = "waiting"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECORDING = "recording"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    COMPANY_CULTURE = "company_culture"
    PROBLEM_SOLVING = "problem_solving"


class Interview(Base):
    """Main interview entity that represents a scheduled interview session"""
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    job_application_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Interview Configuration
    interview_type = Column(String, nullable=False, default=InterviewType.AI_SCREENING)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    timezone = Column(String, default="UTC")
    
    # Status and Progress
    status = Column(String, default=InterviewStatus.SCHEDULED, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI Configuration
    ai_interviewer_persona = Column(String, nullable=True)  # AI personality/role
    difficulty_level = Column(String, default="intermediate")
    focus_areas = Column(ARRAY(String), default=[])  # Skills/areas to focus on
    
    # Technical Settings
    max_questions = Column(Integer, default=10)
    allow_retakes = Column(Boolean, default=False)
    recording_enabled = Column(Boolean, default=True)
    
    # Results Summary
    overall_score = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)  # HIRE, MAYBE, REJECT
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job_application = relationship("JobApplication")
    candidate = relationship("User", foreign_keys=[candidate_id])
    company = relationship("User", foreign_keys=[company_id])
    sessions = relationship("InterviewSession", back_populates="interview", cascade="all, delete-orphan")
    analysis = relationship("InterviewAnalysis", back_populates="interview", uselist=False)


class InterviewSession(Base):
    """Represents an active WebRTC session for an interview"""
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(UUID(as_uuid=True), ForeignKey('interviews.id'), nullable=False)
    
    # Session Management
    session_token = Column(String, unique=True, nullable=False, index=True)
    room_id = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default=SessionStatus.WAITING, index=True)
    
    # Connection Details
    candidate_peer_id = Column(String, nullable=True)
    ai_peer_id = Column(String, nullable=True)
    signaling_server = Column(String, nullable=True)
    
    # Session Timing
    joined_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Technical Metrics
    connection_quality = Column(Float, nullable=True)  # 0.0 to 1.0
    audio_quality = Column(Float, nullable=True)
    video_quality = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    
    # Recording
    recording_url = Column(String, nullable=True)
    recording_duration = Column(Integer, nullable=True)  # seconds
    
    # Error Handling
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    reconnection_attempts = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="sessions")


class InterviewAnalysis(Base):
    """Stores AI analysis results for completed interviews"""
    __tablename__ = "interview_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(UUID(as_uuid=True), ForeignKey('interviews.id'), nullable=False, unique=True)
    
    # Overall Scores (0.0 to 1.0)
    overall_score = Column(Float, nullable=False)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Detailed Analysis
    skill_scores = Column(JSON, nullable=True)  # {"python": 0.8, "sql": 0.6, ...}
    personality_traits = Column(JSON, nullable=True)  # {"openness": 0.7, "conscientiousness": 0.8, ...}
    behavioral_indicators = Column(JSON, nullable=True)  # {"eye_contact": 0.8, "posture": 0.7, ...}
    
    # Speech Analysis
    speech_pace = Column(Float, nullable=True)  # words per minute
    filler_word_count = Column(Integer, default=0)
    clarity_score = Column(Float, nullable=True)
    vocabulary_complexity = Column(Float, nullable=True)
    
    # Video Analysis
    emotion_timeline = Column(JSON, nullable=True)  # Time-series emotion data
    engagement_score = Column(Float, nullable=True)
    eye_contact_percentage = Column(Float, nullable=True)
    gesture_analysis = Column(JSON, nullable=True)
    
    # Question Performance
    questions_answered = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)  # seconds
    question_scores = Column(JSON, nullable=True)  # Individual question performance
    
    # AI Insights
    strengths = Column(ARRAY(String), default=[])
    areas_for_improvement = Column(ARRAY(String), default=[])
    recommendations = Column(Text, nullable=True)
    red_flags = Column(ARRAY(String), default=[])
    
    # Confidence and Reliability
    analysis_confidence = Column(Float, nullable=False, default=0.0)  # AI confidence in analysis
    data_quality_score = Column(Float, nullable=True)  # Quality of audio/video data
    
    # Processing Metadata
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_duration = Column(Float, nullable=True)  # seconds
    ai_model_version = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="analysis")


class InterviewQuestion(Base):
    """Stores questions asked during interviews and candidate responses"""
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(UUID(as_uuid=True), ForeignKey('interviews.id'), nullable=False)
    
    # Question Details
    question_text = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # QuestionCategory enum
    difficulty_level = Column(String, default="intermediate")
    expected_duration = Column(Integer, default=120)  # seconds
    
    # Question Metadata
    question_order = Column(Integer, nullable=False)
    is_follow_up = Column(Boolean, default=False)
    parent_question_id = Column(UUID(as_uuid=True), ForeignKey('interview_questions.id'), nullable=True)
    
    # AI Generation Context
    generated_from_job_requirements = Column(Boolean, default=True)
    skill_focus = Column(ARRAY(String), default=[])
    context_data = Column(JSON, nullable=True)  # Additional context used for generation
    
    # Response Data
    candidate_response = Column(Text, nullable=True)
    response_duration = Column(Float, nullable=True)  # seconds
    response_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Scoring
    response_score = Column(Float, nullable=True)  # 0.0 to 1.0
    scoring_criteria = Column(JSON, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    
    # Audio/Video Analysis for this question
    audio_analysis = Column(JSON, nullable=True)
    video_analysis = Column(JSON, nullable=True)
    
    # Timestamps
    asked_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    interview = relationship("Interview")
    follow_up_questions = relationship("InterviewQuestion", remote_side=[id])