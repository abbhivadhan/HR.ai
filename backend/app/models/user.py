from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class UserType(str, Enum):
    CANDIDATE = "candidate"
    COMPANY = "company"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.CANDIDATE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    mfa_backup_codes = Column(JSON, nullable=True)
    
    # Security fields
    failed_login_attempts = Column(String, default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    job_postings = relationship("JobPosting", back_populates="company")
    applications = relationship("JobApplication", foreign_keys="JobApplication.candidate_id", back_populates="candidate")
    saved_jobs = relationship("SavedJob", back_populates="candidate")
    notifications = relationship("Notification", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user")
    
    # Phase 1 relationships
    resumes = relationship("Resume", back_populates="user")
    scheduling_preference = relationship("SchedulingPreference", back_populates="user", uselist=False)
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    career_plans = relationship("CareerPlan", back_populates="user")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"