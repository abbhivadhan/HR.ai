"""AI Career Coach Service"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from backend.app.models.career_plan import (
    CareerPlan, CoachConversation, SkillGap, CareerMilestone
)
from backend.app.config import settings


class CareerCoachService:
    """AI-powered career coaching service"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
    
    async def create_career_plan(
        self,
        db: Session,
        user_id: int,
        current_role: Optional[str],
        target_role: str,
        target_salary: Optional[float],
        timeline_months: Optional[int]
    ) -> CareerPlan:
        """Create a new career plan"""
        plan = CareerPlan(
            user_id=user_id,
            current_role=current_role,
            target_role=target_role,
            target_salary=target_salary,
            timeline_months=timeline_months
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        # Generate initial skill gap analysis
        await self._analyze_skill_gaps(db, plan)
        
        return plan
    
    async def chat(
        self,
        db: Session,
        conversation_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """Chat with AI career coach"""
        conversation = db.query(CoachConversation).filter(
            CoachConversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Get career plan context
        career_plan = db.query(CareerPlan).filter(
            CareerPlan.id == conversation.career_plan_id
        ).first()
        
        # Build context
        messages = self._build_chat_context(career_plan, conversation.messages)
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        
        # Update conversation
        conversation.messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation.messages.append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(career_plan)
        
        return {
            "message": {
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.utcnow().isoformat()
            },
            "suggestions": suggestions
        }
    
    async def get_career_path_recommendations(
        self,
        db: Session,
        career_plan_id: int
    ) -> List[Dict[str, Any]]:
        """Get AI-powered career path recommendations"""
        career_plan = db.query(CareerPlan).filter(
            CareerPlan.id == career_plan_id
        ).first()
        
        if not career_plan:
            raise ValueError("Career plan not found")
        
        prompt = f"""
        Analyze career progression from {career_plan.current_role or 'current position'} 
        to {career_plan.target_role}. Provide 3 detailed career path recommendations.
        
        For each path, include:
        1. Role title
        2. Description
        3. Required skills (list)
        4. Average salary range
        5. Growth potential (high/medium/low)
        6. Timeline in months
        7. Step-by-step progression
        
        Return as JSON array.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("recommendations", [])
    
    async def get_salary_insights(
        self,
        role: str,
        location: str = "United States",
        experience_level: str = "mid"
    ) -> Dict[str, Any]:
        """Get salary insights for a role"""
        prompt = f"""
        Provide salary insights for {role} in {location} at {experience_level} level.
        
        Include:
        - Minimum salary
        - Maximum salary
        - Median salary
        - Key factors affecting salary
        
        Return as JSON.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _analyze_skill_gaps(
        self,
        db: Session,
        career_plan: CareerPlan
    ):
        """Analyze skill gaps for career transition"""
        prompt = f"""
        Analyze skill gaps for transitioning from {career_plan.current_role or 'current role'} 
        to {career_plan.target_role}.
        
        Identify 5-7 key skills needed, with:
        - Skill name
        - Priority (high/medium/low)
        - Learning resources (3-5 recommendations)
        
        Return as JSON array.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        skills = result.get("skills", [])
        
        for skill_data in skills:
            skill_gap = SkillGap(
                career_plan_id=career_plan.id,
                skill_name=skill_data["name"],
                current_level=1,
                required_level=4,
                priority=skill_data["priority"],
                learning_resources=skill_data.get("resources", [])
            )
            db.add(skill_gap)
        
        db.commit()
    
    def _build_chat_context(
        self,
        career_plan: CareerPlan,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Build chat context with career plan info"""
        system_message = f"""
        You are an expert career coach helping someone transition from 
        {career_plan.current_role or 'their current role'} to {career_plan.target_role}.
        
        Provide actionable advice on:
        - Skill development
        - Job search strategies
        - Resume optimization
        - Interview preparation
        - Networking
        - Career growth
        
        Be supportive, specific, and practical.
        """
        
        context = [{"role": "system", "content": system_message}]
        
        # Add recent conversation history (last 10 messages)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        for msg in recent_messages:
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return context
    
    async def _generate_suggestions(
        self,
        career_plan: CareerPlan
    ) -> List[str]:
        """Generate conversation suggestions"""
        suggestions = [
            "What skills should I focus on first?",
            "How can I improve my resume?",
            "What certifications would help?",
            "How do I prepare for interviews?",
            "What's the typical salary range?"
        ]
        return suggestions[:3]
