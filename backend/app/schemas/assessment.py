from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from ..models.assessment import AssessmentType, QuestionType, DifficultyLevel, AssessmentStatus


# Question schemas
class QuestionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    category: str = Field(..., min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    code_template: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    max_points: float = Field(default=10.0, ge=0)
    time_limit_seconds: Optional[int] = Field(None, ge=0)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    code_template: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    max_points: Optional[float] = Field(None, ge=0)
    time_limit_seconds: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Question(QuestionBase):
    id: UUID
    ai_generated: bool
    generation_prompt: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Assessment schemas
class AssessmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assessment_type: AssessmentType
    duration_minutes: int = Field(default=60, ge=1, le=480)  # Max 8 hours
    passing_score: float = Field(default=70.0, ge=0, le=100)


class AssessmentCreate(AssessmentBase):
    candidate_id: UUID
    job_posting_id: Optional[UUID] = None
    question_ids: List[UUID] = Field(..., min_items=1)


class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[AssessmentStatus] = None


class AssessmentQuestion(BaseModel):
    id: UUID
    question_id: UUID
    order_index: int
    points: float
    time_limit_seconds: Optional[int]
    question: Question

    class Config:
        from_attributes = True


class Assessment(AssessmentBase):
    id: UUID
    candidate_id: UUID
    job_posting_id: Optional[UUID]
    status: AssessmentStatus
    total_questions: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    total_score: Optional[float]
    percentage_score: Optional[float]
    passed: Optional[bool]
    ai_analysis: Optional[Dict[str, Any]]
    skill_scores: Optional[Dict[str, float]]
    created_at: datetime
    updated_at: datetime
    questions: List[AssessmentQuestion] = []

    class Config:
        from_attributes = True


# Response schemas
class AssessmentResponseBase(BaseModel):
    response_text: Optional[str] = None
    selected_options: Optional[List[str]] = None
    code_solution: Optional[str] = None


class AssessmentResponseCreate(AssessmentResponseBase):
    question_id: UUID


class AssessmentResponseUpdate(AssessmentResponseBase):
    pass


class AssessmentResponse(AssessmentResponseBase):
    id: UUID
    assessment_id: UUID
    question_id: UUID
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    time_spent_seconds: Optional[int]
    points_earned: Optional[float]
    is_correct: Optional[bool]
    ai_feedback: Optional[str]
    ai_score_breakdown: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Assessment session schemas
class AssessmentSession(BaseModel):
    assessment: Assessment
    current_question_index: int = 0
    time_remaining_seconds: int
    responses: List[AssessmentResponse] = []


class StartAssessmentResponse(BaseModel):
    assessment_id: UUID
    session_token: str
    expires_at: datetime
    first_question: Question


class SubmitResponseRequest(BaseModel):
    question_id: UUID
    response: AssessmentResponseCreate


class NextQuestionResponse(BaseModel):
    question: Optional[Question]
    question_index: int
    total_questions: int
    time_remaining_seconds: int
    is_last_question: bool


class CompleteAssessmentResponse(BaseModel):
    assessment_id: UUID
    total_score: float
    percentage_score: float
    passed: bool
    skill_scores: Dict[str, float]
    ai_analysis: Dict[str, Any]


# AI Generation schemas
class GenerateQuestionsRequest(BaseModel):
    job_title: str
    required_skills: List[str]
    difficulty_level: DifficultyLevel
    question_count: int = Field(default=10, ge=1, le=50)
    question_types: List[QuestionType] = Field(default=[QuestionType.MULTIPLE_CHOICE])


class AIAnalysisResult(BaseModel):
    overall_score: float
    skill_breakdown: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    confidence_level: float