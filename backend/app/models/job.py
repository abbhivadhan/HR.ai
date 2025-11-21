from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    FILLED = "filled"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class RemoteType(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Association table for job required skills
job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_posting_id', UUID(as_uuid=True), ForeignKey('job_postings.id')),
    Column('skill_id', UUID(as_uuid=True), ForeignKey('skills.id'))
)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Basic Information
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Short summary for listings
    
    # Job Details
    job_type = Column(String, default=JobType.FULL_TIME)
    experience_level = Column(String, nullable=False)  # From profile.py ExperienceLevel
    department = Column(String, nullable=True)
    
    # Location and Remote
    location = Column(String, nullable=True)
    remote_type = Column(String, default=RemoteType.HYBRID)
    
    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="USD")
    benefits = Column(ARRAY(String), default=[])
    
    # Requirements
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    qualifications = Column(Text, nullable=True)
    
    # Application Settings
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    max_applications = Column(Integer, nullable=True)
    application_instructions = Column(Text, nullable=True)
    
    # Status and Visibility
    status = Column(String, default=JobStatus.DRAFT, index=True)
    is_featured = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    
    # SEO and Metadata
    slug = Column(String, unique=True, nullable=True, index=True)
    meta_description = Column(String, nullable=True)
    tags = Column(ARRAY(String), default=[])
    
    # Timestamps
    posted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Analytics
    view_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)
    
    # Relationships
    company = relationship("User", back_populates="job_postings")
    required_skills = relationship("Skill", secondary=job_skills, back_populates="job_postings")
    applications = relationship("JobApplication", back_populates="job_posting", cascade="all, delete-orphan")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Application Details
    status = Column(String, default=ApplicationStatus.PENDING, index=True)
    cover_letter = Column(Text, nullable=True)
    resume_url = Column(String, nullable=True)  # Can override candidate's default resume
    
    # Screening
    screening_questions = Column(Text, nullable=True)  # JSON string of questions and answers
    ai_match_score = Column(Float, nullable=True)  # AI-calculated compatibility score
    recruiter_notes = Column(Text, nullable=True)
    
    # Timeline
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Communication
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    next_followup_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job_posting = relationship("JobPosting", back_populates="applications")
    candidate = relationship("User", foreign_keys=[candidate_id], back_populates="applications")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("User", back_populates="saved_jobs")
    job_posting = relationship("JobPosting")
    
    # Ensure unique constraint
    __table_args__ = (
        {'extend_existing': True},
    )


# Add back_populates to existing models
from .profile import Skill
Skill.job_postings = relationship("JobPosting", secondary=job_skills, back_populates="required_skills")