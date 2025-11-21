"""Portfolio and Video Resume Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.models import Base


class Portfolio(Base):
    """User portfolio"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    video_intro_url = Column(String(500))
    video_duration = Column(Integer)  # seconds
    headline = Column(String(200))
    bio = Column(Text)
    template_id = Column(String(50), default="modern")
    is_public = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="portfolio")
    projects = relationship("PortfolioProject", back_populates="portfolio", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioProject(Base):
    """Portfolio projects"""
    __tablename__ = "portfolio_projects"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    technologies = Column(JSON, default=list)
    media_urls = Column(JSON, default=list)  # images, videos
    code_snippets = Column(JSON, default=list)
    live_url = Column(String(500))
    github_url = Column(String(500))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="projects")


class Achievement(Base):
    """User achievements and badges"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    badge_type = Column(String(100), nullable=False)  # certification, award, milestone
    title = Column(String(200), nullable=False)
    description = Column(Text)
    issuer = Column(String(200))
    date_earned = Column(DateTime)
    verification_url = Column(String(500))
    icon = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="achievements")
