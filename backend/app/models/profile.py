from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class CompanySize(str, Enum):
    STARTUP = "startup"  # 1-10
    SMALL = "small"      # 11-50
    MEDIUM = "medium"    # 51-200
    LARGE = "large"      # 201-1000
    ENTERPRISE = "enterprise"  # 1000+


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    CERTIFICATE = "certificate"


# Association table for candidate skills
candidate_skills = Table(
    'candidate_skills',
    Base.metadata,
    Column('candidate_profile_id', UUID(as_uuid=True), ForeignKey('candidate_profiles.id')),
    Column('skill_id', UUID(as_uuid=True), ForeignKey('skills.id'))
)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)  # e.g., "programming", "soft_skills", "tools"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    
    # Basic Information
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Professional Information
    current_title = Column(String, nullable=True)
    experience_years = Column(Integer, default=0)
    experience_level = Column(String, default=ExperienceLevel.ENTRY)
    
    # Files
    resume_url = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    
    # Preferences
    preferred_locations = Column(ARRAY(String), default=[])
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    remote_preference = Column(String, default="hybrid")  # remote, onsite, hybrid
    availability_date = Column(DateTime(timezone=True), nullable=True)
    
    # Social Links
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    
    # Privacy Settings
    profile_visibility = Column(String, default="public")  # public, private, companies_only
    allow_contact = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    skills = relationship("Skill", secondary=candidate_skills, back_populates="candidates")
    education = relationship("Education", back_populates="candidate_profile", cascade="all, delete-orphan")
    experience = relationship("WorkExperience", back_populates="candidate_profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="candidate_profile", cascade="all, delete-orphan")


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    
    # Company Information
    company_name = Column(String, nullable=False, index=True)
    industry = Column(String, nullable=True)
    company_size = Column(String, default=CompanySize.STARTUP)
    founded_year = Column(Integer, nullable=True)
    
    # Contact Information
    website = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    culture = Column(Text, nullable=True)
    
    # Media
    logo_url = Column(String, nullable=True)
    banner_url = Column(String, nullable=True)
    
    # Social Links
    linkedin_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_document_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="company_profile")


class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_profile_id = Column(UUID(as_uuid=True), ForeignKey('candidate_profiles.id'), nullable=False)
    
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(String, nullable=True)
    level = Column(String, default=EducationLevel.BACHELOR)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, default=False)
    gpa = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="education")


class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_profile_id = Column(UUID(as_uuid=True), ForeignKey('candidate_profiles.id'), nullable=False)
    
    company_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    achievements = Column(ARRAY(String), default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="experience")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_profile_id = Column(UUID(as_uuid=True), ForeignKey('candidate_profiles.id'), nullable=False)
    
    name = Column(String, nullable=False)
    issuing_organization = Column(String, nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    credential_id = Column(String, nullable=True)
    credential_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="certifications")


# Add back_populates to Skill model
Skill.candidates = relationship("CandidateProfile", secondary=candidate_skills, back_populates="skills")