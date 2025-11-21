"""Career Coach Models"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from backend.app.models import Base


class CareerPlan(Base):
    """Career plan for candidates"""
    __tablename__ = "career_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_role = Column(String(200))
    target_role = Column(String(200))
    target_salary = Column(Float)
    timeline_months = Column(Integer)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="career_plans")
    conversations = relationship("CoachConversation", back_populates="career_plan", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="career_plan", cascade="all, delete-orphan")
    milestones = relationship("CareerMilestone", back_populates="career_plan", cascade="all, delete-orphan")


class CoachConversation(Base):
    """AI Coach conversation history"""
    __tablename__ = "coach_conversations"

    id = Column(Integer, primary_key=True, index=True)
    career_plan_id = Column(Integer, ForeignKey("career_plans.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = Column(JSON, default=list)  # List of {role, content, timestamp}
    topic = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    career_plan = relationship("CareerPlan", back_populates="conversations")
    user = relationship("User")


class SkillGap(Base):
    """Identified skill gaps"""
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    career_plan_id = Column(Integer, ForeignKey("career_plans.id"), nullable=False)
    skill_name = Column(String(200), nullable=False)
    current_level = Column(Integer)  # 1-5
    required_level = Column(Integer)  # 1-5
    priority = Column(String(50))  # high, medium, low
    learning_resources = Column(JSON, default=list)
    status = Column(String(50), default="identified")  # identified, learning, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    career_plan = relationship("CareerPlan", back_populates="skill_gaps")


class CareerMilestone(Base):
    """Career plan milestones"""
    __tablename__ = "career_milestones"

    id = Column(Integer, primary_key=True, index=True)
    career_plan_id = Column(Integer, ForeignKey("career_plans.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    career_plan = relationship("CareerPlan", back_populates="milestones")
