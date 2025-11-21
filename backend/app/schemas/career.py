"""Career Coach Schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CareerPlanCreate(BaseModel):
    """Create career plan"""
    current_role: Optional[str] = Field(None, max_length=200)
    target_role: str = Field(..., max_length=200)
    target_salary: Optional[float] = Field(None, ge=0)
    timeline_months: Optional[int] = Field(None, ge=1, le=120)


class CareerPlanUpdate(BaseModel):
    """Update career plan"""
    current_role: Optional[str] = Field(None, max_length=200)
    target_role: Optional[str] = Field(None, max_length=200)
    target_salary: Optional[float] = Field(None, ge=0)
    timeline_months: Optional[int] = Field(None, ge=1, le=120)
    status: Optional[str] = None


class CareerPlanResponse(BaseModel):
    """Career plan response"""
    id: int
    user_id: int
    current_role: Optional[str]
    target_role: str
    target_salary: Optional[float]
    timeline_months: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[datetime] = None


class CoachConversationCreate(BaseModel):
    """Create conversation"""
    career_plan_id: int
    topic: Optional[str] = Field(None, max_length=200)
    initial_message: str


class CoachConversationResponse(BaseModel):
    """Conversation response"""
    id: int
    career_plan_id: int
    user_id: int
    messages: List[Dict[str, Any]]
    topic: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request"""
    conversation_id: int
    message: str


class ChatResponse(BaseModel):
    """Chat response"""
    message: ChatMessage
    suggestions: List[str] = []


class SkillGapCreate(BaseModel):
    """Create skill gap"""
    skill_name: str = Field(..., max_length=200)
    current_level: int = Field(..., ge=1, le=5)
    required_level: int = Field(..., ge=1, le=5)
    priority: str = Field("medium", pattern="^(high|medium|low)$")


class SkillGapUpdate(BaseModel):
    """Update skill gap"""
    current_level: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None


class SkillGapResponse(BaseModel):
    """Skill gap response"""
    id: int
    career_plan_id: int
    skill_name: str
    current_level: int
    required_level: int
    priority: str
    learning_resources: List[Dict[str, Any]]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CareerMilestoneCreate(BaseModel):
    """Create milestone"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None


class CareerMilestoneUpdate(BaseModel):
    """Update milestone"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    completed: Optional[bool] = None


class CareerMilestoneResponse(BaseModel):
    """Milestone response"""
    id: int
    career_plan_id: int
    title: str
    description: Optional[str]
    target_date: Optional[datetime]
    completed: bool
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CareerPathRecommendation(BaseModel):
    """Career path recommendation"""
    role: str
    description: str
    required_skills: List[str]
    average_salary: float
    growth_potential: str
    timeline_months: int
    steps: List[str]


class SalaryInsight(BaseModel):
    """Salary insight"""
    role: str
    min_salary: float
    max_salary: float
    median_salary: float
    location: str
    experience_level: str
