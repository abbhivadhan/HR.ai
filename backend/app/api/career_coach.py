"""Career Coach API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.career_plan import CareerPlan, CoachConversation
from backend.app.schemas.career import (
    CareerPlanCreate, CareerPlanUpdate, CareerPlanResponse,
    CoachConversationCreate, CoachConversationResponse,
    ChatRequest, ChatResponse,
    SkillGapCreate, SkillGapUpdate, SkillGapResponse,
    CareerMilestoneCreate, CareerMilestoneUpdate, CareerMilestoneResponse,
    CareerPathRecommendation, SalaryInsight
)
from backend.app.services.career_coach_service import CareerCoachService

router = APIRouter(prefix="/api/career-coach", tags=["Career Coach"])
coach_service = CareerCoachService()


@router.post("/plans", response_model=CareerPlanResponse)
async def create_career_plan(
    plan_data: CareerPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new career plan"""
    plan = await coach_service.create_career_plan(
        db=db,
        user_id=int(current_user.id),
        current_role=plan_data.current_role,
        target_role=plan_data.target_role,
        target_salary=plan_data.target_salary,
        timeline_months=plan_data.timeline_months
    )
    return plan


@router.get("/plans", response_model=List[CareerPlanResponse])
def get_career_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's career plans"""
    plans = db.query(CareerPlan).filter(
        CareerPlan.user_id == int(current_user.id)
    ).all()
    return plans


@router.get("/plans/{plan_id}", response_model=CareerPlanResponse)
def get_career_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific career plan"""
    plan = db.query(CareerPlan).filter(
        CareerPlan.id == plan_id,
        CareerPlan.user_id == int(current_user.id)
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Career plan not found")
    
    return plan


@router.post("/conversations", response_model=CoachConversationResponse)
def create_conversation(
    conv_data: CoachConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new coaching conversation"""
    # Verify career plan belongs to user
    plan = db.query(CareerPlan).filter(
        CareerPlan.id == conv_data.career_plan_id,
        CareerPlan.user_id == int(current_user.id)
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Career plan not found")
    
    conversation = CoachConversation(
        career_plan_id=conv_data.career_plan_id,
        user_id=int(current_user.id),
        topic=conv_data.topic,
        messages=[]
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.post("/chat", response_model=ChatResponse)
async def chat_with_coach(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI career coach"""
    # Verify conversation belongs to user
    conversation = db.query(CoachConversation).filter(
        CoachConversation.id == chat_request.conversation_id,
        CoachConversation.user_id == int(current_user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    response = await coach_service.chat(
        db=db,
        conversation_id=chat_request.conversation_id,
        user_message=chat_request.message
    )
    
    return response


@router.get("/plans/{plan_id}/recommendations", response_model=List[CareerPathRecommendation])
async def get_career_recommendations(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI career path recommendations"""
    # Verify plan belongs to user
    plan = db.query(CareerPlan).filter(
        CareerPlan.id == plan_id,
        CareerPlan.user_id == int(current_user.id)
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Career plan not found")
    
    recommendations = await coach_service.get_career_path_recommendations(
        db=db,
        career_plan_id=plan_id
    )
    
    return recommendations


@router.get("/salary-insights", response_model=SalaryInsight)
async def get_salary_insights(
    role: str,
    location: str = "United States",
    experience_level: str = "mid",
    current_user: User = Depends(get_current_user)
):
    """Get salary insights for a role"""
    insights = await coach_service.get_salary_insights(
        role=role,
        location=location,
        experience_level=experience_level
    )
    
    return insights


@router.get("/plans/{plan_id}/skill-gaps", response_model=List[SkillGapResponse])
def get_skill_gaps(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill gaps for career plan"""
    # Verify plan belongs to user
    plan = db.query(CareerPlan).filter(
        CareerPlan.id == plan_id,
        CareerPlan.user_id == int(current_user.id)
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Career plan not found")
    
    from backend.app.models.career_plan import SkillGap
    skill_gaps = db.query(SkillGap).filter(
        SkillGap.career_plan_id == plan_id
    ).all()
    
    return skill_gaps
