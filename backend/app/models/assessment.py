from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class AssessmentType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    PERSONALITY = "personality"
    CODING = "coding"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CODING = "coding"
    TEXT_RESPONSE = "text_response"
    TRUE_FALSE = "true_false"
    RATING_SCALE = "rating_scale"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AssessmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.NOT_STARTED)
    duration_minutes = Column(Integer, nullable=False, default=60)
    total_questions = Column(Integer, nullable=False, default=0)
    passing_score = Column(Float, nullable=False, default=70.0)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Scoring
    total_score = Column(Float, nullable=True)
    percentage_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    
    # AI Analysis
    ai_analysis = Column(JSON, nullable=True)
    skill_scores = Column(JSON, nullable=True)  # {"python": 85.5, "algorithms": 92.0}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("User", foreign_keys=[candidate_id])
    job_posting = relationship("JobPosting", foreign_keys=[job_posting_id])
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    responses = relationship("AssessmentResponse", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=False)
    category = Column(String, nullable=False)  # e.g., "python", "algorithms", "system_design"
    tags = Column(JSON, nullable=True)  # ["arrays", "sorting", "optimization"]
    
    # Question configuration
    options = Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    code_template = Column(Text, nullable=True)  # For coding questions
    test_cases = Column(JSON, nullable=True)  # For coding questions
    
    # Scoring
    max_points = Column(Float, nullable=False, default=10.0)
    time_limit_seconds = Column(Integer, nullable=True)
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assessment_questions = relationship("AssessmentQuestion", back_populates="question")


class AssessmentQuestion(Base):
    """Junction table linking assessments to questions with order and customization"""
    __tablename__ = "assessment_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    points = Column(Float, nullable=False)  # Can override question's default points
    time_limit_seconds = Column(Integer, nullable=True)  # Can override question's time limit
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    question = relationship("Question", back_populates="assessment_questions")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    
    # Response data
    response_text = Column(Text, nullable=True)
    selected_options = Column(JSON, nullable=True)  # For multiple choice
    code_solution = Column(Text, nullable=True)  # For coding questions
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Scoring
    points_earned = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    # AI Analysis
    ai_feedback = Column(Text, nullable=True)
    ai_score_breakdown = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("Question")