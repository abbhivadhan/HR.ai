"""AI Resume Builder Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from backend.app.models import Base


class Resume(Base):
    """User resumes"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    template_id = Column(String(50), default="professional")
    content = Column(JSON, default=dict)  # Full resume content
    ats_score = Column(Float)
    keywords = Column(JSON, default=list)
    is_primary = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    exports = relationship("ResumeExport", back_populates="resume", cascade="all, delete-orphan")
    optimizations = relationship("ATSOptimization", back_populates="resume", cascade="all, delete-orphan")


class ResumeExport(Base):
    """Resume export history"""
    __tablename__ = "resume_exports"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    format = Column(String(50), nullable=False)  # pdf, docx, txt
    file_url = Column(String(500))
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="exports")


class ATSOptimization(Base):
    """ATS optimization suggestions"""
    __tablename__ = "ats_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Float, nullable=False)
    suggestions = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)
    formatting_issues = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="optimizations")
    job = relationship("Job")
