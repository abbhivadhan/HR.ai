"""
Job Matching Models

Models for storing job matching scores, recommendations, and analytics.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class RecommendationType(str, Enum):
    AUTOMATIC = "automatic"
    SKILL_UPDATE = "skill_update"
    MANUAL = "manual"
    SIMILAR_CANDIDATES = "similar_candidates"


class InteractionType(str, Enum):
    VIEW = "view"
    SAVE = "save"
    APPLY = "apply"
    SHARE = "share"
    DISMISS = "dismiss"
    CLICK = "click"


class NotificationFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"


class JobMatchScore(Base):
    """
    Stores calculated match scores between candidates and job postings.
    """
    __tablename__ = "job_match_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False, index=True)
    
    # Match scores
    overall_score = Column(Float, nullable=False, index=True)
    skill_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    location_match_score = Column(Float, nullable=True)
    salary_match_score = Column(Float, nullable=True)
    collaborative_score = Column(Float, nullable=True)
    content_based_score = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Match details
    match_reasons = Column(ARRAY(String), nullable=True)
    improvement_suggestions = Column(ARRAY(String), nullable=True)
    
    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    candidate = relationship("User", foreign_keys=[candidate_id])
    job_posting = relationship("JobPosting", foreign_keys=[job_posting_id])
    recommendations = relationship("JobRecommendation", back_populates="match_score", cascade="all, delete-orphan")
    
    # Unique constraint on candidate-job pair
    __table_args__ = (
        {'extend_existing': True},
    )


class JobRecommendation(Base):
    """
    Tracks job recommendations sent to candidates.
    """
    __tablename__ = "job_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False, index=True)
    match_score_id = Column(UUID(as_uuid=True), ForeignKey('job_match_scores.id'), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String, nullable=False, index=True)
    
    # Tracking timestamps
    recommended_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    candidate = relationship("User", foreign_keys=[candidate_id])
    job_posting = relationship("JobPosting", foreign_keys=[job_posting_id])
    match_score = relationship("JobMatchScore", back_populates="recommendations")


class CandidateJobInteraction(Base):
    """
    Tracks candidate interactions with job postings for collaborative filtering.
    """
    __tablename__ = "candidate_job_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False, index=True)
    
    # Interaction details
    interaction_type = Column(String, nullable=False, index=True)
    interaction_value = Column(Float, nullable=True)  # Implicit rating (time spent, etc.)
    interaction_metadata = Column(JSON, nullable=True)  # Additional interaction data
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    candidate = relationship("User", foreign_keys=[candidate_id])
    job_posting = relationship("JobPosting", foreign_keys=[job_posting_id])


class MatchingPreferences(Base):
    """
    User preferences for job matching and notifications.
    """
    __tablename__ = "matching_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True, index=True)
    
    # Notification settings
    notification_frequency = Column(String, default=NotificationFrequency.WEEKLY, nullable=False)
    min_match_score = Column(Float, default=0.6, nullable=False)
    
    # Job preferences
    preferred_job_types = Column(ARRAY(String), nullable=True)
    excluded_companies = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    max_commute_distance = Column(Integer, nullable=True)  # in miles/km
    
    # Matching weights
    salary_importance_weight = Column(Float, default=0.3, nullable=False)
    location_importance_weight = Column(Float, default=0.2, nullable=False)
    skill_importance_weight = Column(Float, default=0.5, nullable=False)
    
    # Matching behavior
    allow_overqualified_matches = Column(Boolean, default=True, nullable=False)
    allow_underqualified_matches = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="matching_preferences")


class JobMatchingAnalytics(Base):
    """
    Analytics data for job matching performance.
    """
    __tablename__ = "job_matching_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False, unique=True, index=True)
    
    # Match statistics
    total_matches_generated = Column(Integer, default=0, nullable=False)
    high_quality_matches = Column(Integer, default=0, nullable=False)  # score >= 0.8
    medium_quality_matches = Column(Integer, default=0, nullable=False)  # 0.6 <= score < 0.8
    low_quality_matches = Column(Integer, default=0, nullable=False)  # score < 0.6
    
    # Recommendation statistics
    total_recommendations_sent = Column(Integer, default=0, nullable=False)
    total_views_from_recommendations = Column(Integer, default=0, nullable=False)
    total_applications_from_recommendations = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    average_match_score = Column(Float, nullable=True)
    recommendation_click_rate = Column(Float, nullable=True)
    recommendation_application_rate = Column(Float, nullable=True)
    
    # Timestamps
    last_calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    job_posting = relationship("JobPosting", back_populates="matching_analytics")


# Add back_populates to existing models
from .user import User
from .job import JobPosting

User.matching_preferences = relationship("MatchingPreferences", back_populates="user", uselist=False)
JobPosting.matching_analytics = relationship("JobMatchingAnalytics", back_populates="job_posting", uselist=False)